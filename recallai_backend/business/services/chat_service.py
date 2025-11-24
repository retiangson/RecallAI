from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from openai import OpenAI
import base64
import mimetypes

from recallai_backend.core.config import settings
from recallai_backend.domain.repositories.conversation_repository import ConversationRepository
from recallai_backend.domain.repositories.note_repository import NoteRepository
from recallai_backend.domain.interfaces.i_conversation_repository import IConversationRepository
from recallai_backend.domain.interfaces.i_note_repository import INoteRepository
from recallai_backend.business.services.embedding_service import EmbeddingService
from recallai_backend.business.interfaces.i_chat_service import IChatService
from recallai_backend.utils.file_extractor import extract_text_gpt
from recallai_backend.contracts.chat_dtos import ChatResponseDTO, ChatAnswerSource, ChatRequestDTO

client = OpenAI(api_key=settings.openai_api_key)

IMAGE_EXTS = ["png", "jpg", "jpeg", "gif", "webp"]


def is_image(filename: str, mime: str) -> bool:
    ext = filename.lower().split(".")[-1]
    return ext in IMAGE_EXTS or (mime and mime.startswith("image/"))


class ChatService(IChatService):
    # ==========================================================
    # INITIALIZATION
    # ==========================================================
    def __init__(
        self,
        db: Optional[Session] = None,
        embedding_service: Optional[EmbeddingService] = None,
        conv_repo: Optional[IConversationRepository] = None,
        note_repo: Optional[INoteRepository] = None,
    ):
        """
        For DI/installer:
            pass conv_repo, note_repo, embedding_service.

        For legacy usage:
            pass db (+ embedding_service) and repos will be constructed internally.
        """
        if conv_repo is not None and note_repo is not None:
            self.repo_conv: IConversationRepository = conv_repo
            self.repo_notes: INoteRepository = note_repo
        else:
            if db is None:
                raise ValueError("Either (conv_repo & note_repo) or db must be provided to ChatService.")
            self.repo_conv = ConversationRepository(db)
            self.repo_notes = NoteRepository(db)

        if embedding_service is not None:
            self.embedding = embedding_service
        else:
            # Fallback for legacy
            self.embedding = EmbeddingService()

    # ==========================================================
    # TEXT-ONLY CHAT → USED BY /api/v1/chat
    # ==========================================================
    def ask(self, dto: ChatRequestDTO) -> ChatResponseDTO:
        """
        Pure text chat with RAG notes.
        """

        # ⭐ FIXED: Use dto.prompt (matches frontend)
        user_text = (dto.prompt or "").strip()

        if not user_text:
            return ChatResponseDTO(
                answer="I didn’t receive any message.",
                sources=[]
            )

        # Create or load conversation
        if dto.conversation_id is None:
            title = user_text[:50] if user_text else "New conversation"
            conv = self.repo_conv.create_conversation(dto.user_id, title)
            conversation_id = conv.id
        else:
            conversation_id = dto.conversation_id

        # Save new user message
        user_msg = self.repo_conv.add_message(conversation_id, "user", user_text)

        # Load conversation history (oldest → newest)
        history = self.repo_conv.get_messages_paginated(
            conversation_id,
            limit=1000,
            before_id=None
        )

        message_history = [
            {"role": m.role, "content": m.content}
            for m in history
        ]

        # Load history (DESC from repository)
        history = self.repo_conv.get_messages_paginated(
            conversation_id,
            limit=1000,
            before_id=None
        )

        # ⭐ FIX: Reverse to ASC for GPT
        history = list(reversed(history))

        message_history = [
            {"role": m.role, "content": m.content}
            for m in history
        ]
        
        # RAG notes retrieval
        query_vec = self.embedding.embed_text(user_text)
        notes = self.repo_notes.search_by_vector(query_vec, top_k=dto.top_k)

        sources: List[ChatAnswerSource] = []
        rag_text_blocks = []

        for n in notes:
            snippet = n.content[:200] + "..."
            sources.append(
                ChatAnswerSource(note_id=n.id, title=n.title, snippet=snippet)
            )
            rag_text_blocks.append(f"[NOTE {n.id}]\n{n.content}")

        # System instructions
        system_blocks = [
            {
                "role": "system",
                "content": (
                    "You are RecallAI. You answer based on:\n"
                    "1. User messages\n"
                    "2. Their personal notes (RAG)\n"
                    "Reply clearly and concisely."
                ),
            }
        ]

        if rag_text_blocks:
            system_blocks.append(
                {
                    "role": "system",
                    "content": "--- NOTES CONTEXT ---\n" + "\n\n".join(rag_text_blocks),
                }
            )

        messages = system_blocks + message_history

        # GPT Response
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        answer = completion.choices[0].message.content

        # Save AI message and return its ID to the frontend
        assistant_msg = self.repo_conv.add_message(
            conversation_id, "assistant", answer
        )

        return ChatResponseDTO(
            answer=answer,
            sources=sources,
            message_id=assistant_msg.id
        )



    # ==========================================================
    # FILE + PROMPT CHAT → USED BY /chat/upload endpoint
    # ==========================================================
    async def handle_file_upload(
        self,
        conversation_id: int,
        prompt: str,
        files: List[UploadFile],
    ) -> ChatResponseDTO:

        prompt = prompt.strip() or "Please analyze the attached file(s) in detail."

        content_blocks = [{"type": "text", "text": prompt}]
        attachment_log: List[str] = []

        for file in files:
            filename = file.filename or "file"
            mime = (
                file.content_type
                or mimetypes.guess_type(filename)[0]
                or "application/octet-stream"
            )

            file_bytes = await file.read()

            if is_image(filename, mime):
                b64 = base64.b64encode(file_bytes).decode()
                image_url = f"data:{mime};base64,{b64}"

                content_blocks.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    }
                )
                attachment_log.append(f"- {filename} (image)")

            elif filename.lower().endswith(".pdf"):
                uploaded = client.files.create(
                    file=(filename, file_bytes, mime),
                    purpose="vision",
                )

                content_blocks.append({"type": "file", "file": {"file_id": uploaded.id}})
                attachment_log.append(f"- {filename} (pdf → file_id {uploaded.id})")

            else:
                extracted_text = extract_text_gpt(file_bytes, filename)
                content_blocks.append(
                    {
                        "type": "text",
                        "text": f"FILE: {filename}\n\n{extracted_text}",
                    }
                )
                attachment_log.append(f"- {filename} (document extracted locally)")

        combined_message = "Attached files:\n" + "\n".join(attachment_log) + f"\n\nPrompt:\n{prompt}"
        self.repo_conv.add_message(conversation_id, "user", combined_message)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are RecallAI. Use the prompt and all attached files.",
                },
                {
                    "role": "user",
                    "content": content_blocks,
                },
            ],
        )

        answer = completion.choices[0].message.content
        self.repo_conv.add_message(conversation_id, "assistant", answer)

        return ChatResponseDTO(answer=answer, sources=[])

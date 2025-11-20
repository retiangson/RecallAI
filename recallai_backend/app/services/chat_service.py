from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from openai import OpenAI
import base64
import mimetypes

from app.core.config import settings
from app.domain.repositories.conversation_repository import ConversationRepository
from app.domain.repositories.note_repository import NoteRepository
from app.services.embedding_service import EmbeddingService
from app.utils.file_extractor import extract_text_gpt
from app.dtos.chat_dtos import ChatResponseDTO, ChatAnswerSource

client = OpenAI(api_key=settings.openai_api_key)


IMAGE_EXTS = ["png", "jpg", "jpeg", "gif", "webp"]


def is_image(filename: str, mime: str) -> bool:
    ext = filename.lower().split(".")[-1]
    return ext in IMAGE_EXTS or (mime and mime.startswith("image/"))


class ChatService:

    # ==========================================================
    # INITIALIZATION
    # ==========================================================
    def __init__(self, db: Session, embedding_service: EmbeddingService):
        self.db = db
        self.repo_conv = ConversationRepository(db)
        self.repo_notes = NoteRepository(db)
        self.embedding = embedding_service

    # ==========================================================
    # TEXT-ONLY CHAT → USED BY /api/v1/chat
    # ==========================================================
    def ask(self, dto) -> ChatResponseDTO:
        """
        Pure text chat with RAG notes.
        """

        # Create or load conversation
        if dto.conversation_id is None:
            conv = self.repo_conv.create_conversation(dto.prompt[:50])
            conversation_id = conv.id
        else:
            conversation_id = dto.conversation_id

        # Save user message
        self.repo_conv.add_message(conversation_id, "user", dto.prompt)

        # Conversation history
        history = self.repo_conv.get_messages(conversation_id)
        message_history = [{"role": m.role, "content": m.content} for m in history]

        # RAG notes retrieval
        query_vec = self.embedding.embed_text(dto.prompt)
        notes = self.repo_notes.search_by_vector(query_vec, top_k=dto.top_k)

        sources: List[ChatAnswerSource] = []
        rag_text_blocks = []

        for n in notes:
            snippet = n.content[:200] + "..."
            sources.append(ChatAnswerSource(note_id=n.id, title=n.title, snippet=snippet))
            rag_text_blocks.append(f"[NOTE {n.id}]\n{n.content}")

        system_blocks = [
            {
                "role": "system",
                "content": (
                    "You are RecallAI. You answer using:\n"
                    "1. User messages\n"
                    "2. Their personal notes (RAG)\n"
                )
            }
        ]

        if rag_text_blocks:
            system_blocks.append({
                "role": "system",
                "content": "\n\n--- NOTES CONTEXT ---\n" + "\n\n".join(rag_text_blocks)
            })

        # Build full message list
        messages = system_blocks + message_history

        # OpenAI call
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        answer = completion.choices[0].message.content

        self.repo_conv.add_message(conversation_id, "assistant", answer)

        return ChatResponseDTO(answer=answer, sources=sources)

    # ==========================================================
    # FILE + PROMPT CHAT → USED BY /chat/upload endpoint
    # ==========================================================
    async def handle_file_upload(
        self,
        conversation_id: int,
        prompt: str,
        files: List[UploadFile]
    ) -> ChatResponseDTO:

        prompt = prompt.strip() or "Please analyze the attached file(s) in detail."

        # Start with user prompt block
        content_blocks = [
            { "type": "text", "text": prompt }
        ]

        attachment_log = []

        for file in files:
            filename = file.filename or "file"
            mime = (
                file.content_type
                or mimetypes.guess_type(filename)[0]
                or "application/octet-stream"
            )

            file_bytes = await file.read()

            # -----------------------------------------------------
            # CASE 1 — IMAGE → base64 → image_url (correct schema)
            # -----------------------------------------------------
            if is_image(filename, mime):
                b64 = base64.b64encode(file_bytes).decode()
                image_url = f"data:{mime};base64,{b64}"

                content_blocks.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                })

                attachment_log.append(f"- {filename} (image)")

            # -----------------------------------------------------
            # CASE 2 — PDF → Upload & reference as type="file"
            # -----------------------------------------------------
            elif filename.lower().endswith(".pdf"):
                uploaded = client.files.create(
                    file=(filename, file_bytes, mime),
                    purpose="vision"
                )

                content_blocks.append({
                    "type": "file",
                    "file": { "file_id": uploaded.id }
                })

                attachment_log.append(f"- {filename} (pdf → file_id {uploaded.id})")

            # -----------------------------------------------------
            # CASE 3 — DOCX / PPTX / XLSX / TXT → local extract
            # -----------------------------------------------------
            else:
                extracted_text = extract_text_gpt(file_bytes, filename)

                content_blocks.append({
                    "type": "text",
                    "text": f"FILE: {filename}\n\n{extracted_text}"
                })

                attachment_log.append(f"- {filename} (document extracted locally)")

        # Store readable user entry in conversation
        combined_message = (
            "Attached files:\n" +
            "\n".join(attachment_log) +
            f"\n\nPrompt:\n{prompt}"
        )

        self.repo_conv.add_message(conversation_id, "user", combined_message)

        # Call OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are RecallAI. Use the prompt and all attached files."
                },
                {
                    "role": "user",
                    "content": content_blocks
                }
            ]
        )

        answer = completion.choices[0].message.content

        self.repo_conv.add_message(conversation_id, "assistant", answer)

        return ChatResponseDTO(answer=answer, sources=[])

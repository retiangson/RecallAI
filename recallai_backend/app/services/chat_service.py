from typing import List
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import settings
from app.domain.repositories.note_repository import NoteRepository
from app.domain.repositories.conversation_repository import ConversationRepository
from app.services.embedding_service import EmbeddingService
from app.dtos.chat_dtos import ChatRequestDTO, ChatResponseDTO, ChatAnswerSource

client = OpenAI(api_key=settings.openai_api_key)


class ChatService:
    def __init__(self, db: Session, embedding_service: EmbeddingService):
        self.db = db
        self.repo_notes = NoteRepository(db)
        self.repo_conv = ConversationRepository(db)
        self.embedding_service = embedding_service

    def ask(self, dto: ChatRequestDTO) -> ChatResponseDTO:

        # ----------------------------
        # 1️⃣ Ensure conversation exists
        # ----------------------------
        if dto.conversation_id is None:
            conv = self.repo_conv.create_conversation(title=dto.question[:50])
            conversation_id = conv.id
        else:
            conversation_id = dto.conversation_id

        # Save user message
        self.repo_conv.add_message(conversation_id, "user", dto.question)

        # ----------------------------
        # 2️⃣ Get conversation history
        # ----------------------------
        history = self.repo_conv.get_messages(conversation_id)

        message_history = [
            {"role": m.role, "content": m.content}
            for m in history
        ]

        # ----------------------------
        # 3️⃣ Get relevant notes using Vector Search
        # ----------------------------
        query_vec = self.embedding_service.embed_text(dto.question)
        notes = self.repo_notes.search_by_vector(query_vec, top_k=dto.top_k)

        sources: List[ChatAnswerSource] = []
        context_chunks: List[str] = []

        for n in notes:
            snippet = n.content[:200] + "..."
            sources.append(
                ChatAnswerSource(note_id=n.id, title=n.title, snippet=snippet)
            )
            context_chunks.append(f"[Note {n.id}] {n.content}")

        rag_block = "\n\n".join(context_chunks) if context_chunks else ""

        # ----------------------------
        # 4️⃣ Build OpenAI messages
        # ----------------------------
        system_msg = {
            "role": "system",
            "content": (
                "You are RecallAI, a personal assistant. "
                "You MUST answer using BOTH:\n"
                "1. The conversation history\n"
                "2. The user's notes (context)\n\n"
                "If the answer is not in the notes, or conversation, say 'I don't know'."
            )
        }

        full_messages = [system_msg]

        if rag_block:
            full_messages.append({"role": "system", "content": "RAG Notes:\n" + rag_block})

        full_messages.extend(message_history)

        # ----------------------------
        # 5️⃣ Get OpenAI response
        # ----------------------------
        completion = client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=full_messages,
        )

        answer = completion.choices[0].message.content

        # Save assistant response
        self.repo_conv.add_message(conversation_id, "assistant", answer)

        return ChatResponseDTO(
            answer=answer,
            sources=sources,
        )

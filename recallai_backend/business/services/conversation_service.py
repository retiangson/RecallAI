from typing import Any, Optional, List
from sqlalchemy.orm import Session

from recallai_backend.domain.repositories.conversation_repository import ConversationRepository
from recallai_backend.domain.repositories.note_repository import NoteRepository
from recallai_backend.domain.interfaces.i_conversation_repository import IConversationRepository
from recallai_backend.domain.interfaces.i_note_repository import INoteRepository
from recallai_backend.business.services.embedding_service import EmbeddingService
from recallai_backend.business.interfaces.i_conversation_service import IConversationService


class ConversationService(IConversationService):
    def __init__(
        self,
        db: Optional[Session] = None,
        conv_repo: Optional[IConversationRepository] = None,
        note_repo: Optional[INoteRepository] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        """
        For DI/installer:
            pass conv_repo, note_repo, embedding_service (+ optionally db).

        For legacy:
            pass db only and we construct repositories + embedding service internally.
        """
        self.db = db

        if conv_repo is not None:
            self.repo: IConversationRepository = conv_repo
        else:
            if db is None:
                raise ValueError("Either db or conv_repo must be provided to ConversationService.")
            self.repo = ConversationRepository(db)

        if note_repo is not None:
            self.note_repo: INoteRepository = note_repo
        else:
            if db is None:
                # Only needed when add_message_to_note is used
                self.note_repo = None  # type: ignore[assignment]
            else:
                self.note_repo = NoteRepository(db)

        self.embedding = embedding_service or EmbeddingService()

    # LIST conversations for a user
    def list_for_user(self, user_id: int) -> list[dict[str, Any]]:
        conversations = self.repo.get_for_user(user_id)

        return [
            {
                "id": conv.id,
                "title": conv.title,
                "messages": [
                    {"role": m.role, "content": m.content}
                    for m in conv.messages
                ],
            }
            for conv in conversations
        ]

    # CREATE conversation
    def create(self, user_id: int, title: str | None = None) -> dict[str, Any]:
        conv = self.repo.create_conversation(user_id, title)
        return {"id": conv.id, "title": conv.title, "messages": []}

    # ADD message
    def add_message(self, conv_id: int, role: str, content: str) -> dict[str, Any]:
        msg = self.repo.add_message(conv_id, role, content)
        return {"id": msg.id, "role": msg.role, "content": msg.content}

    # GET by id
    def get_by_id(self, conv_id: int) -> dict[str, Any] | None:
        conv = self.repo.get_by_id(conv_id)
        if not conv:
            return None

        return {
            "id": conv.id,
            "title": conv.title,
            "messages": [
                {"role": m.role, "content": m.content}
                for m in conv.messages
            ],
        }

    # RENAME
    def rename(self, conv_id: int, title: str) -> dict[str, Any] | None:
        conv = self.repo.rename(conv_id, title)
        if not conv:
            return None
        return {"id": conv.id, "title": conv.title}

    # DELETE
    def delete(self, conv_id: int) -> bool:
        return self.repo.delete(conv_id)

    # PAGINATED messages
    def get_messages_paginated(
        self,
        conv_id: int,
        limit: int = 10,
        before_id: int | None = None,
    ) -> list[dict[str, Any]]:
        messages = self.repo.get_messages_paginated(conv_id, limit, before_id)
        messages.sort(key=lambda m: m.id)

        return [
            {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at,
            }
            for msg in messages
        ]

    # Delete single message
    def delete_message(self, message_id: int) -> bool:
        return self.repo.delete_message(message_id)

    # Add message content as a note
    def add_message_to_note(
        self,
        user_id: int,
        content: str,
        title: str | None = None,
    ) -> dict[str, Any]:
        if self.note_repo is None or self.db is None:
            raise ValueError("Note repository and db are required for add_message_to_note.")

        note_title = title or "Chat Snippet"

        note = self.note_repo.create_note(
            user_id=user_id,
            title=note_title,
            content=content,
            source="chat",
        )

        vector = self.embedding.embed_text(content)
        self.note_repo.save_embedding(note.id, vector)

        self.db.commit()

        return {"id": note.id, "title": note_title}

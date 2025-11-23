from sqlalchemy.orm import Session
from recallai_backend.domain.repositories.conversation_repository import ConversationRepository
from recallai_backend.domain.repositories.note_repository import NoteRepository
from recallai_backend.services.embedding_service import EmbeddingService


class ConversationService:
    def __init__(self, db: Session):
        self.repo = ConversationRepository(db)

    # ─────────────────────────────────────────────
    # Get all conversations for a user
    # ─────────────────────────────────────────────
    def list_for_user(self, user_id: int):
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

    # ─────────────────────────────────────────────
    # Create conversation
    # ─────────────────────────────────────────────
    def create(self, user_id: int, title: str | None = None):
        conv = self.repo.create_conversation(user_id, title)
        return {
            "id": conv.id,
            "title": conv.title,
            "messages": [],
        }

    # ─────────────────────────────────────────────
    # Add a message to conversation
    # ─────────────────────────────────────────────
    def add_message(self, conv_id: int, role: str, content: str):
        msg = self.repo.add_message(conv_id, role, content)
        return {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
        }

    # ─────────────────────────────────────────────
    # Get a single conversation
    # ─────────────────────────────────────────────
    def get_by_id(self, conv_id: int):
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

    # ─────────────────────────────────────────────
    # Rename conversation
    # ─────────────────────────────────────────────
    def rename(self, conv_id: int, title: str):
        conv = self.repo.rename(conv_id, title)
        if not conv:
            return None
        return {"id": conv.id, "title": conv.title}

    # ─────────────────────────────────────────────
    # Delete conversation
    # ─────────────────────────────────────────────
    def delete(self, conv_id: int):
        return self.repo.delete(conv_id)

    def get_messages(self, conversation_id: int, limit: int = 10, before_id: int | None = None):
        messages = self.repo.get_messages_paginated(conversation_id, limit, before_id)

        messages.sort(key=lambda m: m.id)  # oldest → newest for UI

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
    
    def delete_message(self, message_id: int):
        return self.repo.delete_message(message_id)
    
    def add_message_to_note(self, user_id: int, content: str, title: str):
        notes = NoteRepository(self.db)
        embed = EmbeddingService()

        # 1. Create note
        note = notes.create_note(
            user_id=user_id,
            title=title,
            content=content,
            source="chat"
        )

        # 2. Embed
        vector = embed.embed_text(content)
        notes.save_embedding(note.id, vector)

        self.db.commit()

        return {"id": note.id, "title": title}
    
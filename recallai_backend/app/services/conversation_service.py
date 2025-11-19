from sqlalchemy.orm import Session
from app.domain.repositories.conversation_repository import ConversationRepository


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

    def get_messages(self, conversation_id: int):
        messages = self.repo.get_messages(conversation_id)

        # Order by ID ascending (oldest → newest)
        messages.sort(key=lambda m: m.id)

        # Convert to DTOs
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
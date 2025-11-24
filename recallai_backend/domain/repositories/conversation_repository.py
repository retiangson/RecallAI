from sqlalchemy.orm import Session, joinedload
from traitlets import List
from recallai_backend.domain.models.conversation import Conversation
from recallai_backend.domain.models.message import Message

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    # ─────────────────────────────────────────────
    # Create a new conversation (user required)
    # ─────────────────────────────────────────────
    def create_conversation(self, user_id: int, title: str | None = None) -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    # ─────────────────────────────────────────────
    # Add a message to a conversation
    # ─────────────────────────────────────────────
    def add_message(self, conv_id: int, role: str, content: str) -> Message:
        msg = Message(conversation_id=conv_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    # ─────────────────────────────────────────────
    # Get messages of a conversation
    # ─────────────────────────────────────────────
    def get_messages(self, conv_id: int) -> List[Message]:
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conv_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    # ─────────────────────────────────────────────
    # Get all conversations for a user
    # Includes messages if needed
    # ─────────────────────────────────────────────
    def get_for_user(self, user_id: int):
        return (
            self.db.query(Conversation)
            .options(joinedload(Conversation.messages))
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.id.desc())
            .all()
        )

    # ─────────────────────────────────────────────
    # Get a single conversation by ID
    # ─────────────────────────────────────────────
    def get_by_id(self, conv_id: int) -> Conversation | None:
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conv_id)
            .first()
        )

    # ─────────────────────────────────────────────
    # Rename conversation
    # ─────────────────────────────────────────────
    def rename(self, conv_id: int, title: str):
        conv = self.get_by_id(conv_id)
        if conv:
            conv.title = title
            self.db.commit()
            self.db.refresh(conv)
        return conv

    # ─────────────────────────────────────────────
    # Delete conversation (cascade deletes messages)
    # ─────────────────────────────────────────────
    def delete(self, conv_id: int):
        conv = self.get_by_id(conv_id)
        if conv:
            self.db.delete(conv)
            self.db.commit()
            return True
        return False

    # ─────────────────────────────────────────────
    # Get paginated messages for a conversation
    # ─────────────────────────────────────────────
    def get_messages_paginated(self, conv_id: int, limit: int, before_id: int | None):
        """
        Return messages newest → oldest for pagination.
        ChatService will reverse them for GPT.
        """
        query = (
            self.db.query(Message)
            .filter(Message.conversation_id == conv_id)
        )

        if before_id:
            query = query.filter(Message.id < before_id)

        return (
            query.order_by(Message.id.desc())   # ⭐ REVERTED BACK TO DESC
                .limit(limit)
                .all()
        )

    
    # ─────────────────────────────────────────────
    # Delete a single message by ID
    # ─────────────────────────────────────────────    
    def delete_message(self, message_id: int):
        msg = (
            self.db.query(Message)
            .filter(Message.id == message_id)
            .first()
        )

        if not msg:
            return False

        self.db.delete(msg)
        self.db.commit()
        return True
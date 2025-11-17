from sqlalchemy.orm import Session
from app.domain.models.conversation import Conversation
from app.domain.models.message import Message

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, title: str = None) -> Conversation:
        conv = Conversation(title=title)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def add_message(self, conv_id: int, role: str, content: str) -> Message:
        msg = Message(conversation_id=conv_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages(self, conv_id: int):
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conv_id)
            .order_by(Message.created_at.asc())
            .all()
        )

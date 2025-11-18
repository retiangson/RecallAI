from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.db import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String(20))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # FIXED relationship - match back_populates
    conversation = relationship("Conversation", back_populates="messages")

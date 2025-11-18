from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to Embedding
    embedding = relationship(
        "Embedding",
        back_populates="note",
        uselist=False,
        cascade="all, delete"
    )

    # Relationship to User
    user = relationship("User")

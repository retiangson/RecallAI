from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.core.db import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)  # e.g. filename or category
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to Embedding (one-to-one)
    embedding = relationship(
        "Embedding",
        back_populates="note",
        uselist=False,         # important: one embedding per note
        cascade="all, delete"  # optional: delete embedding when note is deleted
    )

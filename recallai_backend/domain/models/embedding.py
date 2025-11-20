from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from recallai_backend.core.db import Base
from recallai_backend.domain.models.vector_type import VectorType


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), unique=True)

    # FIXED: Use custom VectorType for Supabase vector extension
    vector = Column(VectorType(1536))

    note = relationship("Note", back_populates="embedding")

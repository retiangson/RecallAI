from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session

# Repository interfaces
from recallai_backend.domain.interfaces.i_user_repository import IUserRepository
from recallai_backend.domain.interfaces.i_note_repository import INoteRepository
from recallai_backend.domain.interfaces.i_conversation_repository import IConversationRepository

# Concrete repositories
from recallai_backend.domain.repositories.user_repository import UserRepository
from recallai_backend.domain.repositories.note_repository import NoteRepository
from recallai_backend.domain.repositories.conversation_repository import ConversationRepository

# Embedding
from recallai_backend.business.services.embedding_service import EmbeddingService


class DomainInstaller:
    """
    TRANSIENT Domain Installer.
    Creates a NEW instance for every request:
        - New repositories
        - New DB session (injected)
        - New embedding service
    """

    def __init__(self, db: Session):
        # DB is NOW supplied externally (FastAPI Depends)
        self._db = db

    # ─────────────────────────────────────────────
    # DB Session
    # ─────────────────────────────────────────────
    def get_db(self) -> Session:
        return self._db

    # ─────────────────────────────────────────────
    # Embedding Service
    # ─────────────────────────────────────────────
    def get_embedding_service(self) -> EmbeddingService:
        # EmbeddingService is stateless → safe as transient
        return EmbeddingService()

    # ─────────────────────────────────────────────
    # Repositories (Transient)
    # ─────────────────────────────────────────────
    def get_user_repository(self) -> IUserRepository:
        return UserRepository(self._db)

    def get_note_repository(self) -> INoteRepository:
        return NoteRepository(self._db)

    def get_conversation_repository(self) -> IConversationRepository:
        return ConversationRepository(self._db)

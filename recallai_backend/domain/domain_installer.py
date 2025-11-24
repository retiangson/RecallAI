from __future__ import annotations
from typing import Optional

from sqlalchemy.orm import Session

from recallai_backend.core.db import SessionLocal

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
    The ROOT of all domain-layer dependency creation.
    This class is responsible for:
        - Creating DB sessions
        - Creating repositories (interfaces)
        - Creating embedding services
        - Managing lifetime of domain resources
    """

    def __init__(self, db: Optional[Session] = None):
        self._db = db or SessionLocal()

    # ─────────────────────────────────────────────
    # DB Session
    # ─────────────────────────────────────────────
    def get_db(self) -> Session:
        return self._db

    # ─────────────────────────────────────────────
    # Embedding Service
    # ─────────────────────────────────────────────
    def get_embedding_service(self) -> EmbeddingService:
        return EmbeddingService()

    # ─────────────────────────────────────────────
    # Repositories (Domain Interfaces)
    # ─────────────────────────────────────────────
    def get_user_repository(self) -> IUserRepository:
        return UserRepository(self._db)

    def get_note_repository(self) -> INoteRepository:
        return NoteRepository(self._db)

    def get_conversation_repository(self) -> IConversationRepository:
        return ConversationRepository(self._db)

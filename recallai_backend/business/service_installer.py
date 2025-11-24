from __future__ import annotations

from typing import Type, Dict, Any

from recallai_backend.domain.domain_installer import DomainInstaller

# Service Interfaces
from recallai_backend.business.interfaces.i_auth_service import IAuthService
from recallai_backend.business.interfaces.i_chat_service import IChatService
from recallai_backend.business.interfaces.i_note_service import INoteService
from recallai_backend.business.interfaces.i_conversation_service import IConversationService


class ServiceInstaller:
    """
    TRANSIENT DI CONTAINER
    -----------------------------------------
    A new instance of each service is created
    EVERY TIME it's requested.

    FIXES:
    - No global DB sessions
    - No shared services
    - No SQLAlchemy concurrency errors
    """

    def __init__(self, domain: DomainInstaller):
        self._domain = domain

    # ─────────────────────────────────────────────
    # TRANSIENT SERVICE FACTORIES
    # ─────────────────────────────────────────────
    def get_auth_service(self) -> IAuthService:
        from recallai_backend.business.services.auth_service import AuthService

        return AuthService(
            user_repo=self._domain.get_user_repository(),
            db=self._domain.get_db(),
        )

    def get_chat_service(self) -> IChatService:
        from recallai_backend.business.services.chat_service import ChatService

        return ChatService(
            conv_repo=self._domain.get_conversation_repository(),
            note_repo=self._domain.get_note_repository(),
            embedding_service=self._domain.get_embedding_service(),
            db=self._domain.get_db(),
        )

    def get_note_service(self) -> INoteService:
        from recallai_backend.business.services.note_service import NoteService

        return NoteService(
            note_repo=self._domain.get_note_repository(),
            embedding_service=self._domain.get_embedding_service(),
            db=self._domain.get_db(),
        )

    def get_conversation_service(self) -> IConversationService:
        from recallai_backend.business.services.conversation_service import ConversationService

        return ConversationService(
            conv_repo=self._domain.get_conversation_repository(),
            note_repo=self._domain.get_note_repository(),
            embedding_service=self._domain.get_embedding_service(),
            db=self._domain.get_db(),
        )

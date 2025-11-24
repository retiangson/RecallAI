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
    Enterprise-grade Dependency Injection Container.
    This is the SINGLE source of truth for all business services.
    """

    def __init__(self, domain: DomainInstaller):
        """
        DI requires domain installer (repositories, db, embedding).
        """
        self._domain = domain
        self._service_map: Dict[Type, Any] = {}

        self._register_services()

    # ─────────────────────────────────────────────
    # REGISTER SERVICES
    # ─────────────────────────────────────────────
    def _register_services(self) -> None:
        """
        Bind all service interfaces to their implementations.
        Uses lazy imports to avoid circular dependencies.
        """

        # Lazy imports to avoid circular references
        from recallai_backend.business.services.auth_service import AuthService
        from recallai_backend.business.services.chat_service import ChatService
        from recallai_backend.business.services.note_service import NoteService
        from recallai_backend.business.services.conversation_service import ConversationService

        # Domain dependencies
        user_repo = self._domain.get_user_repository()
        note_repo = self._domain.get_note_repository()
        conv_repo = self._domain.get_conversation_repository()
        embedding_service = self._domain.get_embedding_service()

        db = self._domain.get_db()

        # Auth Service → requires UserRepo
        self._service_map[IAuthService] = AuthService(
            user_repo=user_repo,
            db=db,
        )

        # Chat Service → requires ConversationRepo + NoteRepo + Embedding
        self._service_map[IChatService] = ChatService(
            conv_repo=conv_repo,
            note_repo=note_repo,
            embedding_service=embedding_service,
            db=db,
        )

        # Note Service → requires NoteRepo + Embedding
        self._service_map[INoteService] = NoteService(
            note_repo=note_repo,
            embedding_service=embedding_service,
            db=db,
        )

        # Conversation Service → requires ConversationRepo + NoteRepo + Embedding
        self._service_map[IConversationService] = ConversationService(
            conv_repo=conv_repo,
            note_repo=note_repo,
            embedding_service=embedding_service,
            db=db,
        )

    # ─────────────────────────────────────────────
    # RESOLVE ANY SERVICE BY INTERFACE
    # ─────────────────────────────────────────────
    def resolve(self, interface: Type) -> Any:
        """
        Resolve a service instance by interface.
        Raises ValueError if service was not registered.
        """
        if interface in self._service_map:
            return self._service_map[interface]

        raise ValueError(f"Service not registered for interface: {interface}")

    # ─────────────────────────────────────────────
    # CONVENIENCE GETTERS (like KaiHelper)
    # ─────────────────────────────────────────────
    def get_auth_service(self) -> IAuthService:
        return self.resolve(IAuthService)

    def get_chat_service(self) -> IChatService:
        return self.resolve(IChatService)

    def get_note_service(self) -> INoteService:
        return self.resolve(INoteService)

    def get_conversation_service(self) -> IConversationService:
        return self.resolve(IConversationService)

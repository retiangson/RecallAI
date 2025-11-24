# recallai_backend/core/service_installer.py

from recallai_backend.services.auth_service import AuthService
from recallai_backend.services.note_service import NoteService
from recallai_backend.services.chat_service import ChatService
from recallai_backend.services.conversation_service import ConversationService
from recallai_backend.core.repository_installer import RepositoryInstaller


class ServiceInstaller:
    """
    Pure service construction.
    Accepts repositories from RepositoryInstaller.
    No DB access here.
    """

    def __init__(self, repos: RepositoryInstaller):
        self.repos = repos

    def get_auth_service(self):
        return AuthService(self.repos.users)

    def get_note_service(self):
        return NoteService(self.repos.notes)

    def get_chat_service(self):
        return ChatService(self.repos.conversations, self.repos.notes)

    def get_conversation_service(self):
        return ConversationService(self.repos.conversations, self.repos.notes)

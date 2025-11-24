# recallai_backend/core/repository_installer.py

from sqlalchemy.orm import Session

from recallai_backend.domain.repositories.user_repository import UserRepository
from recallai_backend.domain.repositories.note_repository import NoteRepository
from recallai_backend.domain.repositories.conversation_repository import ConversationRepository


class RepositoryInstaller:
    """
    Creates repository instances using the DB session.
    Only this layer touches the DB.
    """

    def __init__(self, db: Session):
        self.users = UserRepository(db)
        self.notes = NoteRepository(db)
        self.conversations = ConversationRepository(db)

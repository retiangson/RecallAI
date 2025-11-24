from fastapi import Depends
from sqlalchemy.orm import Session

from recallai_backend.core.db import get_db
from recallai_backend.domain.domain_installer import DomainInstaller
from recallai_backend.business.service_installer import ServiceInstaller


class RequestContainer:
    """
    A request-scoped DI container.
    Each request gets:
        - fresh db session
        - fresh domain installer
        - fresh service installer

    Controllers depend on this instead of passing db manually.
    """

    def __init__(self, db: Session):
        self.domain = DomainInstaller(db)
        self.services = ServiceInstaller(self.domain)

    # SERVICE SHORTCUTS
    def notes(self):
        return self.services.get_note_service()

    def chat(self):
        return self.services.get_chat_service()

    def bulk(self):
        return self.services.get_note_service()

    def conversations(self):
        return self.services.get_conversation_service()

    def auth(self):
        return self.services.get_auth_service()


def get_request_container(
    db: Session = Depends(get_db),
) -> RequestContainer:
    return RequestContainer(db)

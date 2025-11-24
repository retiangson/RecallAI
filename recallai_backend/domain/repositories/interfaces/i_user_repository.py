from typing import Protocol, Optional
from recallai_backend.domain.models.user_model import User


class IUserRepository(Protocol):
    def get_by_email(self, email: str) -> Optional[User]:
        ...

    def get_by_id(self, user_id: int) -> Optional[User]:
        ...

    def create_user(self, email: str, password_hash: str) -> User:
        ...

from typing import Protocol, Optional
from recallai_backend.domain.models.user_model import User


class IUserRepository(Protocol):
    """
    Abstraction for user persistence operations.
    """

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email if it exists.
        """
        ...

    def create(self, email: str, password: str) -> User:
        """
        Create a new user with email + hashed password.
        """
        ...

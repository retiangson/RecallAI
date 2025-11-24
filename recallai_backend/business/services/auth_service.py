from typing import Optional
from sqlalchemy.orm import Session

from recallai_backend.domain.repositories.user_repository import UserRepository
from recallai_backend.domain.interfaces.i_user_repository import IUserRepository
from recallai_backend.contracts.auth_dtos import RegisterDTO, LoginDTO, UserResponse
from recallai_backend.business.interfaces.i_auth_service import IAuthService


class AuthService(IAuthService):
    def __init__(
        self,
        db: Optional[Session] = None,
        user_repo: Optional[IUserRepository] = None,
    ):
        """
        Best-practice constructor:

        - For DI/installer: pass a IUserRepository instance.
        - For legacy usage: pass a db and let the service create UserRepository.
        """
        if user_repo is not None:
            self.repo: IUserRepository = user_repo
        else:
            if db is None:
                raise ValueError("Either db or user_repo must be provided to AuthService.")
            self.repo = UserRepository(db)

    def register(self, dto: RegisterDTO) -> UserResponse:
        existing = self.repo.get_by_email(dto.email)
        if existing:
            raise ValueError("Email already registered")

        user = self.repo.create(dto.email, dto.password)
        return UserResponse(id=user.id, email=user.email)

    def login(self, dto: LoginDTO) -> UserResponse:
        user = self.repo.get_by_email(dto.email)
        if not user or user.password != dto.password:
            raise ValueError("Invalid email or password")

        return UserResponse(id=user.id, email=user.email)

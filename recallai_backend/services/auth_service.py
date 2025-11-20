from sqlalchemy.orm import Session
from recallai_backend.domain.repositories.user_repository import UserRepository
from recallai_backend.dtos.auth_dtos import RegisterDTO, LoginDTO, UserResponse

class AuthService:
    def __init__(self, db: Session):
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

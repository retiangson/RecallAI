from typing import Protocol
from recallai_backend.contracts.auth_dtos import RegisterDTO, LoginDTO, UserResponse


class IAuthService(Protocol):
    def register(self, dto: RegisterDTO) -> UserResponse:
        ...

    def login(self, dto: LoginDTO) -> UserResponse:
        ...

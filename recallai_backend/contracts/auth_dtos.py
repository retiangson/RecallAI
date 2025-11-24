# recallai_backend/contracts/auth_dtos.py

from pydantic import BaseModel


class RegisterDTO(BaseModel):
    email: str
    password: str


class LoginDTO(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str

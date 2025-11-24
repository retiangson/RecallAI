"""
Auth-related DTOs (contracts) used by the API and service layers.

Thin wrapper around `recallai_backend.dtos.auth_dtos`.
"""

from recallai_backend.dtos.auth_dtos import (
    RegisterDTO,
    LoginDTO,
    UserResponse,
)

__all__ = ["RegisterDTO", "LoginDTO", "UserResponse"]

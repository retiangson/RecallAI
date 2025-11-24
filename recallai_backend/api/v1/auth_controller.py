from fastapi import APIRouter, HTTPException, Depends

from recallai_backend.di.request_container import (
    RequestContainer,
    get_request_container,
)
from recallai_backend.contracts.auth_dtos import RegisterDTO, LoginDTO, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(
    dto: RegisterDTO,
    c: RequestContainer = Depends(get_request_container)
):
    try:
        return c.auth().register(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=UserResponse)
def login(
    dto: LoginDTO,
    c: RequestContainer = Depends(get_request_container)
):
    try:
        return c.auth().login(dto)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid email or password")

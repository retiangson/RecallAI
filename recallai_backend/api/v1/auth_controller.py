from fastapi import APIRouter, HTTPException

from recallai_backend.bootstrap import container
from recallai_backend.contracts.auth_dtos import RegisterDTO, LoginDTO, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(dto: RegisterDTO):
    service = container.get_auth_service()
    try:
        return service.register(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=UserResponse)
def login(dto: LoginDTO):
    service = container.get_auth_service()
    try:
        return service.login(dto)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid email or password")

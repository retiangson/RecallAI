from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from recallai_backend.core.dependencies import get_db
from recallai_backend.services.auth_service import AuthService
from recallai_backend.dtos.auth_dtos import RegisterDTO, LoginDTO, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(dto: RegisterDTO, db: Session = Depends(get_db)):
    try:
        return AuthService(db).register(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=UserResponse)
def login(dto: LoginDTO, db: Session = Depends(get_db)):
    try:
        return AuthService(db).login(dto)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid email or password")

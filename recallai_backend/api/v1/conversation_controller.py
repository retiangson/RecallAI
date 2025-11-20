from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from recallai_backend.core.dependencies import get_db
from recallai_backend.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversation", tags=["conversation"])


# ────────────────────────────────
# DTOs
# ────────────────────────────────
class UserID(BaseModel):
    user_id: int

class CreateConvDTO(BaseModel):
    user_id: int

class ConvID(BaseModel):
    conversation_id: int

class RenameDTO(BaseModel):
    conversation_id: int
    title: str

class DeleteDTO(BaseModel):
    conversation_id: int


# ────────────────────────────────
# Endpoints
# ────────────────────────────────

@router.post("/list")
def list_conversations(dto: UserID, db: Session = Depends(get_db)):
    service = ConversationService(db)
    return service.list_for_user(dto.user_id)


@router.post("/create")
def create_conversation(dto: CreateConvDTO, db: Session = Depends(get_db)):
    service = ConversationService(db)
    conv = service.repo.create_conversation(dto.user_id)
    return {
        "id": conv.id,
        "title": conv.title,
        "messages": []
    }


@router.post("/messages")
def get_messages(dto: ConvID, db: Session = Depends(get_db)):
    service = ConversationService(db)
    return service.get_messages(dto.conversation_id)


@router.post("/rename")
def rename_conversation(dto: RenameDTO, db: Session = Depends(get_db)):
    service = ConversationService(db)
    return service.rename(dto.conversation_id, dto.title)


@router.post("/delete")
def delete_conversation(dto: DeleteDTO, db: Session = Depends(get_db)):
    service = ConversationService(db)
    return service.delete(dto.conversation_id)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_embedding_service
from app.dtos.chat_dtos import ChatRequestDTO, ChatResponseDTO
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponseDTO)
def ask(
    dto: ChatRequestDTO,
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service),
):
    service = ChatService(db, emb)
    return service.ask(dto)

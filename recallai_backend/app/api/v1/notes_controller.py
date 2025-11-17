from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_embedding_service
from app.dtos.note_dtos import NoteCreateDTO, NoteResponseDTO
from app.services.note_service import NoteService

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponseDTO)
def create_note(
    dto: NoteCreateDTO,
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service),
):
    service = NoteService(db, emb)
    return service.create_note(dto)

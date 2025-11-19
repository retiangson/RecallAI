from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_embedding_service

from app.dtos.note_dtos import (
    NoteCreateDTO, 
    NoteUpdateDTO, 
    NoteDeleteDTO,
    NoteGetDTO,
    NoteListDTO,
    NoteSearchDTO,
    NoteResponseDTO
)

from app.services.note_service import NoteService

router = APIRouter(prefix="/notes", tags=["notes"])


# ─────────────────────────────────────────────
# CREATE NOTE
# ─────────────────────────────────────────────
@router.post("", response_model=NoteResponseDTO)
def create_note(
    dto: NoteCreateDTO,
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service),
):
    service = NoteService(db, emb)
    return service.create_note(dto)


# ─────────────────────────────────────────────
# GET NOTE BY ID
# ─────────────────────────────────────────────
@router.post("/get", response_model=NoteResponseDTO | None)
def get_note(
    dto: NoteGetDTO,
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service)
):
    service = NoteService(db, emb)
    return service.get_note(dto.note_id)


# ─────────────────────────────────────────────
# LIST NOTES FOR USER
# ─────────────────────────────────────────────
@router.post("/list")
def list_notes(
    dto: NoteListDTO,
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service)
):
    service = NoteService(db, emb)
    return service.list_notes(dto.user_id)


# ─────────────────────────────────────────────
# UPDATE NOTE
# ─────────────────────────────────────────────
@router.post("/update", response_model=NoteResponseDTO | None)
def update_note(
    dto: NoteUpdateDTO,
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service)
):
    service = NoteService(db, emb)
    return service.update_note(dto)


# ─────────────────────────────────────────────
# DELETE NOTE
# ─────────────────────────────────────────────
@router.post("/delete")
def delete_note(
    dto: NoteDeleteDTO,
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service)
):
    service = NoteService(db, emb)
    return service.delete_note(dto.note_id)


# ─────────────────────────────────────────────
# VECTOR SEARCH
# ─────────────────────────────────────────────
@router.post("/search")
def search_notes(
    dto: NoteSearchDTO,
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service)
):
    service = NoteService(db, emb)
    return service.search_notes(dto.vector, dto.top_k)

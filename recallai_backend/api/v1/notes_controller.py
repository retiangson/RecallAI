from fastapi import APIRouter

from recallai_backend.bootstrap import container
from recallai_backend.contracts.note_dtos import (
    NoteCreateDTO,
    NoteGetDTO,
    NoteListDTO,
    NoteUpdateDTO,
    NoteDeleteDTO,
    NoteSearchDTO,
    NoteResponseDTO,
)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponseDTO)
def create_note(dto: NoteCreateDTO):
    service = container.get_note_service()
    return service.create_note(dto)


@router.post("/get", response_model=NoteResponseDTO | None)
def get_note(dto: NoteGetDTO):
    service = container.get_note_service()
    return service.get_note(dto.note_id)


@router.post("/list")
def list_notes(dto: NoteListDTO):
    service = container.get_note_service()
    return service.list_notes(dto.user_id)


@router.post("/update", response_model=NoteResponseDTO | None)
def update_note(dto: NoteUpdateDTO):
    service = container.get_note_service()
    return service.update_note(dto)


@router.post("/delete")
def delete_note(dto: NoteDeleteDTO):
    service = container.get_note_service()
    return service.delete_note(dto.note_id)


@router.post("/search")
def search_notes(dto: NoteSearchDTO):
    service = container.get_note_service()
    return service.search_notes(dto.vector, dto.top_k)

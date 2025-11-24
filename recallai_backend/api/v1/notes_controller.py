from fastapi import APIRouter, Depends

from recallai_backend.di.request_container import (
    RequestContainer,
    get_request_container,
)
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
def create_note(dto: NoteCreateDTO, c: RequestContainer = Depends(get_request_container)):
    return c.notes().create_note(dto)


@router.post("/get", response_model=NoteResponseDTO | None)
def get_note(dto: NoteGetDTO, c: RequestContainer = Depends(get_request_container)):
    return c.notes().get_note(dto.note_id)


@router.post("/list")
def list_notes(dto: NoteListDTO, c: RequestContainer = Depends(get_request_container)):
    return c.notes().list_notes(dto.user_id)


@router.post("/update", response_model=NoteResponseDTO | None)
def update_note(dto: NoteUpdateDTO, c: RequestContainer = Depends(get_request_container)):
    return c.notes().update_note(dto)


@router.post("/delete")
def delete_note(dto: NoteDeleteDTO, c: RequestContainer = Depends(get_request_container)):
    return c.notes().delete_note(dto.note_id)


@router.post("/search")
def search_notes(dto: NoteSearchDTO, c: RequestContainer = Depends(get_request_container)):
    return c.notes().search_notes(dto.vector, dto.top_k)

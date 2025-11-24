from typing import Protocol, List
from recallai_backend.contracts.note_dtos import (
    NoteCreateDTO,
    NoteUpdateDTO,
    NoteResponseDTO,
)


class INoteService(Protocol):
    def create_note(self, dto: NoteCreateDTO) -> NoteResponseDTO:
        ...

    def get_note(self, note_id: int) -> NoteResponseDTO | None:
        ...

    def list_notes(self, user_id: int) -> List[NoteResponseDTO]:
        ...

    def update_note(self, dto: NoteUpdateDTO) -> NoteResponseDTO | None:
        ...

    def delete_note(self, note_id: int) -> bool:
        ...

    def search_notes(self, vector: list[float], top_k: int = 5) -> list[dict]:
        ...

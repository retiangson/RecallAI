from typing import Protocol, List, Optional
from recallai_backend.domain.models.note import Note


class INoteRepository(Protocol):
    def create_note(self, user_id: int, title: str | None, content: str, source: str | None) -> Note:
        ...

    def get_note(self, note_id: int) -> Optional[Note]:
        ...

    def list_notes(self, user_id: int) -> List[Note]:
        ...

    def update_note(self, note_id: int, title: str | None, content: str | None) -> Optional[Note]:
        ...

    def delete_note(self, note_id: int) -> bool:
        ...

    def search_notes(self, vector: list[float], top_k: int) -> list[dict]:
        ...

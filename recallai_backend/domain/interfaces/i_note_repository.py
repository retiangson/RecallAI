from typing import Protocol, List, Optional
from recallai_backend.domain.models.note import Note
from recallai_backend.domain.models.embedding import Embedding


class INoteRepository(Protocol):
    """
    Abstraction for notes and vector embeddings persistence.
    """

    # CREATE
    def create_note(
        self,
        user_id: int,
        title: str | None,
        content: str,
        source: str | None,
    ) -> Note:
        ...

    def save_embedding(self, note_id: int, vector: list[float]) -> Embedding:
        ...

    # READ
    def get_by_id(self, note_id: int) -> Optional[Note]:
        ...

    def get_for_user(self, user_id: int) -> List[Note]:
        ...

    # UPDATE
    def update_note(
        self,
        note_id: int,
        title: str | None,
        content: str | None,
    ) -> Optional[Note]:
        ...

    # DELETE
    def delete_note(self, note_id: int) -> bool:
        ...

    # VECTOR SEARCH
    def search_by_vector(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> List[Note]:
        ...

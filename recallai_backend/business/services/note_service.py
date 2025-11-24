from typing import Optional, List
from sqlalchemy.orm import Session

from recallai_backend.domain.repositories.note_repository import NoteRepository
from recallai_backend.domain.interfaces.i_note_repository import INoteRepository
from recallai_backend.business.services.embedding_service import EmbeddingService
from recallai_backend.business.interfaces.i_note_service import INoteService
from recallai_backend.contracts.note_dtos import (
    NoteCreateDTO,
    NoteUpdateDTO,
    NoteResponseDTO,
)


class NoteService(INoteService):
    """
    Best-Practice Note Service:
    - Handles CRUD + vector search
    - Embeddings optional: generated ONLY when explicitly requested
    """

    def __init__(
        self,
        db: Optional[Session] = None,
        embedding_service: Optional[EmbeddingService] = None,
        note_repo: Optional[INoteRepository] = None,
    ):
        """
        For DI/installer:
            pass note_repo + embedding_service (and optionally db if you want manual commits).

        For legacy:
            pass db (+ optional embedding_service) and we construct NoteRepository ourselves.
        """
        self.db = db  # kept for commit/refresh logic

        if note_repo is not None:
            self.repo: INoteRepository = note_repo
        else:
            if db is None:
                raise ValueError("Either db or note_repo must be provided to NoteService.")
            self.repo = NoteRepository(db)

        self.embedding_service = embedding_service

    # CREATE
    def create_note(self, dto: NoteCreateDTO) -> NoteResponseDTO:
        note = self.repo.create_note(
            user_id=dto.user_id,
            title=dto.title,
            content=dto.content,
            source=dto.source,
        )

        if self.embedding_service:
            vector = self.embedding_service.embed_text(dto.content)
            self.repo.save_embedding(note.id, vector)

        if self.db:
            self.db.commit()
            self.db.refresh(note)

        return NoteResponseDTO.model_validate(note)

    # GET single
    def get_note(self, note_id: int) -> NoteResponseDTO | None:
        note = self.repo.get_by_id(note_id)
        if not note:
            return None
        return NoteResponseDTO.model_validate(note)

    # LIST all
    def list_notes(self, user_id: int) -> List[NoteResponseDTO]:
        notes = self.repo.get_for_user(user_id)
        return [NoteResponseDTO.model_validate(n) for n in notes]

    # UPDATE
    def update_note(self, dto: NoteUpdateDTO) -> NoteResponseDTO | None:
        note = self.repo.update_note(dto.note_id, dto.title, dto.content)
        if not note:
            return None

        if dto.content is not None and self.embedding_service:
            vector = self.embedding_service.embed_text(dto.content)
            self.repo.save_embedding(note.id, vector)

        if self.db:
            self.db.commit()
            self.db.refresh(note)

        return NoteResponseDTO.model_validate(note)

    # DELETE
    def delete_note(self, note_id: int) -> bool:
        return self.repo.delete_note(note_id)

    # SEARCH
    def search_notes(self, vector: list[float], top_k: int = 5):
        notes = self.repo.search_by_vector(vector, top_k)
        return [NoteResponseDTO.model_validate(n) for n in notes]

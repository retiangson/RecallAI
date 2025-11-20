from sqlalchemy.orm import Session
from app.domain.repositories.note_repository import NoteRepository
from app.dtos.note_dtos import NoteCreateDTO, NoteUpdateDTO, NoteResponseDTO
from app.services.embedding_service import EmbeddingService


class NoteService:
    """
    Best-Practice Note Service:
    - Handles CRUD only
    - Embeddings optional: generated ONLY when explicitly requested
    - Does NOT auto-embed on note creation (important for bulk uploads)
    """

    def __init__(self, db: Session, embedding_service: EmbeddingService = None):
        self.repo = NoteRepository(db)
        self.embedding_service = embedding_service
        self.db = db

    # ─────────────────────────────────────────────
    # CREATE NOTE (NO automatic embeddings)
    # ─────────────────────────────────────────────
    def create_note(self, dto: NoteCreateDTO) -> NoteResponseDTO:
        note = self.repo.create_note(
            user_id=dto.user_id,
            title=dto.title,
            content=dto.content,
            source=dto.source
        )

        # Only generate embeddings if service is available
        if self.embedding_service:
            vector = self.embedding_service.embed_text(dto.content)
            self.repo.save_embedding(note.id, vector)

        self.db.commit()
        self.db.refresh(note)
        return NoteResponseDTO.model_validate(note)

    # ─────────────────────────────────────────────
    # GET single note
    # ─────────────────────────────────────────────
    def get_note(self, note_id: int) -> NoteResponseDTO | None:
        note = self.repo.get_by_id(note_id)
        if not note:
            return None
        return NoteResponseDTO.model_validate(note)

    # ─────────────────────────────────────────────
    # LIST all notes for a user
    # ─────────────────────────────────────────────
    def list_notes(self, user_id: int):
        notes = self.repo.get_for_user(user_id)
        return [NoteResponseDTO.model_validate(n) for n in notes]

    # ─────────────────────────────────────────────
    # UPDATE note (title + content)
    # ─────────────────────────────────────────────
    def update_note(self, dto: NoteUpdateDTO) -> NoteResponseDTO | None:
        note = self.repo.update_note(dto.note_id, dto.title, dto.content)
        if not note:
            return None

        # Regenerate embeddings ONLY if service is provided
        if dto.content is not None and self.embedding_service:
            vector = self.embedding_service.embed_text(dto.content)
            self.repo.save_embedding(note.id, vector)

        self.db.commit()
        self.db.refresh(note)
        return NoteResponseDTO.model_validate(note)

    # ─────────────────────────────────────────────
    # DELETE note (+ embeddings)
    # ─────────────────────────────────────────────
    def delete_note(self, note_id: int) -> bool:
        return self.repo.delete_note(note_id)

    # ─────────────────────────────────────────────
    # VECTOR SEARCH (only works if embeddings exist)
    # ─────────────────────────────────────────────
    def search_notes(self, vector: list[float], top_k: int = 5):
        notes = self.repo.search_by_vector(vector, top_k)
        return [NoteResponseDTO.model_validate(n) for n in notes]

from sqlalchemy.orm import Session
from app.domain.repositories.note_repository import NoteRepository
from app.dtos.note_dtos import NoteCreateDTO, NoteResponseDTO
from app.services.embedding_service import EmbeddingService


class NoteService:
    def __init__(self, db: Session, embedding_service: EmbeddingService):
        self.repo = NoteRepository(db)
        self.embedding_service = embedding_service
        self.db = db

    def create_note(self, dto: NoteCreateDTO) -> NoteResponseDTO:
        note = self.repo.create_note(dto.user_id, dto.title, dto.content, dto.source)

        vector = self.embedding_service.embed_text(dto.content)
        self.repo.save_embedding(note.id, vector)

        self.db.commit()
        self.db.refresh(note)

        return NoteResponseDTO.model_validate(note)

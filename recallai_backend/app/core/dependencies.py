from app.core.db import SessionLocal
from app.services.embedding_service import EmbeddingService


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_embedding_service():
    return EmbeddingService()

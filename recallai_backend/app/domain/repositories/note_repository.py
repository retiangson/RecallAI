from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.domain.models.note import Note
from app.domain.models.embedding import Embedding


class NoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_note(self, title: str | None, content: str, source: str | None) -> Note:
        note = Note(title=title, content=content, source=source)
        self.db.add(note)
        self.db.flush()  # get note.id without commit yet
        return note

    def save_embedding(self, note_id: int, vector: list[float]) -> Embedding:
        # vector stored as pgvector (text("vector(1536)"))
        emb = Embedding(note_id=note_id, vector=vector)
        self.db.add(emb)
        return emb

    def search_by_vector(self, query_vector: list[float], top_k: int = 5) -> List[Note]:
        """
        Uses pgvector <-> similarity search.
        Neon requires explicit casting: vector('[..]')
        """

        # Convert Python list → pgvector string "[1,2,3]"
        embedding_str = "[" + ",".join(str(x) for x in query_vector) + "]"

        sql = text("""
            SELECT n.*
            FROM embeddings e
            JOIN notes n ON n.id = e.note_id
            ORDER BY e.vector <-> vector(:embedding)
            LIMIT :top_k
        """)

        result = self.db.execute(
            sql,
            {
                "embedding": embedding_str,
                "top_k": top_k,
            }
        )

        return result.scalars().all()

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.domain.models.note import Note
from app.domain.models.embedding import Embedding

class NoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_note(self, user_id: int, title: str | None, content: str, source: str | None) -> Note:
        note = Note(user_id=user_id, title=title, content=content, source=source)
        self.db.add(note)
        self.db.flush()
        return note

    def save_embedding(self, note_id: int, vector: list[float]) -> Embedding:
        emb = Embedding(note_id=note_id, vector=vector)
        self.db.add(emb)
        return emb

    def search_by_vector(self, query_vector: list[float], top_k: int = 5) -> List[Note]:
        """
        FIXED: RETURN REAL NOTE OBJECTS, NOT INTEGERS
        """

        # Convert Python list to pgvector string
        embedding_str = "[" + ",".join(str(x) for x in query_vector) + "]"

        sql = text("""
            SELECT n.id
            FROM embeddings e
            JOIN notes n ON n.id = e.note_id
            ORDER BY e.vector <-> vector(:embedding)
            LIMIT :top_k
        """)

        rows = self.db.execute(
            sql,
            {"embedding": embedding_str, "top_k": top_k}
        ).fetchall()

        note_ids = [r[0] for r in rows]

        if not note_ids:
            return []

        # fetch ORM Note objects
        notes = self.db.query(Note).filter(Note.id.in_(note_ids)).all()

        # preserve order
        note_map = {n.id: n for n in notes}
        ordered_notes = [note_map[nid] for nid in note_ids if nid in note_map]

        return ordered_notes

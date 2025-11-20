from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from recallai_backend.domain.models.note import Note
from recallai_backend.domain.models.embedding import Embedding

class NoteRepository:
    def __init__(self, db: Session):
        self.db = db

    # ─────────────────────────────────────────────
    # CREATE Note
    # ─────────────────────────────────────────────
    def create_note(self, user_id: int, title: str | None, content: str, source: str | None) -> Note:
        note = Note(user_id=user_id, title=title, content=content, source=source)
        self.db.add(note)
        self.db.flush()  # Needed to get ID before embedding
        return note

    # ─────────────────────────────────────────────
    # UPSERT embedding (fix duplicate key error)
    # ─────────────────────────────────────────────
    def save_embedding(self, note_id: int, vector: list[float]) -> Embedding:
        sql = text("""
            INSERT INTO embeddings (note_id, vector)
            VALUES (:note_id, :vector)
            ON CONFLICT (note_id)
            DO UPDATE SET vector = EXCLUDED.vector
            RETURNING id
        """)

        row = self.db.execute(
            sql,
            {"note_id": note_id, "vector": vector}
        ).fetchone()

        # Return ORM object for the embedding
        return self.db.query(Embedding).filter(Embedding.id == row[0]).first()

    # ─────────────────────────────────────────────
    # GET a single note
    # ─────────────────────────────────────────────
    def get_by_id(self, note_id: int) -> Note | None:
        return self.db.query(Note).filter(Note.id == note_id).first()

    # ─────────────────────────────────────────────
    # GET all notes for a user
    # ─────────────────────────────────────────────
    def get_for_user(self, user_id: int) -> List[Note]:
        return (
            self.db.query(Note)
            .filter(Note.user_id == user_id)
            .order_by(Note.id.desc())
            .all()
        )

    # ─────────────────────────────────────────────
    # UPDATE note title/content
    # ─────────────────────────────────────────────
    def update_note(self, note_id: int, title: str | None, content: str):
        note = self.get_by_id(note_id)
        if not note:
            return None

        if title is not None:
            note.title = title
        if content is not None:
            note.content = content

        self.db.commit()
        self.db.refresh(note)
        return note

    # ─────────────────────────────────────────────
    # DELETE note + embedding
    # ─────────────────────────────────────────────
    def delete_note(self, note_id: int) -> bool:
        note = self.get_by_id(note_id)
        if not note:
            return False

        # Delete embeddings first
        self.db.query(Embedding).filter(Embedding.note_id == note_id).delete()

        # Delete note
        self.db.delete(note)
        self.db.commit()
        return True

    # ─────────────────────────────────────────────
    # VECTOR SEARCH
    # ─────────────────────────────────────────────
    def search_by_vector(self, query_vector: list[float], top_k: int = 5) -> List[Note]:
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

        notes = self.db.query(Note).filter(Note.id.in_(note_ids)).all()
        note_map = {n.id: n for n in notes}

        return [note_map[nid] for nid in note_ids if nid in note_map]

from __future__ import annotations

import re
from typing import List
from dataclasses import dataclass
from sqlalchemy.orm import Session

from recallai_backend.services.embedding_service import EmbeddingService
from recallai_backend.domain.repositories.note_repository import NoteRepository
from recallai_backend.dtos.note_dtos import NoteCreateDTO


# ─────────────────────────────────────────────
# CLEAN TEXT (pure, no GPT)
# ─────────────────────────────────────────────
def clean_text(text: str) -> str:
    if not text:
        return ""

    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse 3+ newlines → 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing spaces
    lines = [ln.rstrip() for ln in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()


# ─────────────────────────────────────────────
# CHUNK TEXT FOR VECTORS (best-practice)
# ─────────────────────────────────────────────
def chunk_text(
    text: str,
    max_chars: int = 2500,     # good for GPT-4o-embed
    overlap: int = 400
) -> List[str]:

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == length:
            break

        start = max(0, end - overlap)

    return chunks


# ─────────────────────────────────────────────
# INGESTION PIPELINE: text → chunks → embedding → DB
# ─────────────────────────────────────────────
def ingest_text(
    *,
    db: Session,
    embedding_service: EmbeddingService,
    note_repo: NoteRepository,
    user_id: int,
    source_filename: str,
    raw_text: str
) -> List[int]:
    """
    Returns list of created note IDs.
    """

    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned)

    created_ids = []

    for idx, chunk in enumerate(chunks):
        title = f"{source_filename} (part {idx + 1})"

        # 1. Create note row
        dto = NoteCreateDTO(
            user_id=user_id,
            title=title,
            content=chunk,
            source=source_filename,
        )
        note = note_repo.create_note(
            user_id=dto.user_id,
            title=dto.title,
            content=dto.content,
            source=dto.source
        )

        # 2. Embed immediately
        vector = embedding_service.embed_text(chunk)
        note_repo.save_embedding(note.id, vector)

        created_ids.append(note.id)

    db.commit()

    return created_ids

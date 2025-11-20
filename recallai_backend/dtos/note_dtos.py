from pydantic import BaseModel
from typing import Optional, List


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────
class NoteCreateDTO(BaseModel):
    user_id: int
    title: Optional[str] = None
    content: str
    source: Optional[str] = None


# ─────────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────────
class NoteResponseDTO(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    content: str
    source: Optional[str]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# GET NOTE
# ─────────────────────────────────────────────
class NoteGetDTO(BaseModel):
    note_id: int


# ─────────────────────────────────────────────
# LIST NOTES
# ─────────────────────────────────────────────
class NoteListDTO(BaseModel):
    user_id: int


# ─────────────────────────────────────────────
# UPDATE NOTE
# ─────────────────────────────────────────────
class NoteUpdateDTO(BaseModel):
    note_id: int
    title: Optional[str] = None
    content: Optional[str] = None


# ─────────────────────────────────────────────
# DELETE NOTE
# ─────────────────────────────────────────────
class NoteDeleteDTO(BaseModel):
    note_id: int


# ─────────────────────────────────────────────
# VECTOR SEARCH
# ─────────────────────────────────────────────
class NoteSearchDTO(BaseModel):
    vector: List[float]
    top_k: int = 5

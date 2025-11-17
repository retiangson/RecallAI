from pydantic import BaseModel
from typing import Optional


class NoteCreateDTO(BaseModel):
    title: Optional[str] = None
    content: str
    source: Optional[str] = None


class NoteResponseDTO(BaseModel):
    id: int
    title: Optional[str]
    content: str
    source: Optional[str]

    class Config:
        from_attributes = True

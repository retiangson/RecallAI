from pydantic import BaseModel
from typing import List, Optional


class ChatRequestDTO(BaseModel):
    conversation_id: int | None = None
    question: str
    top_k: int = 5


class ChatAnswerSource(BaseModel):
    note_id: int
    title: Optional[str]
    snippet: str


class ChatResponseDTO(BaseModel):
    answer: str
    sources: List[ChatAnswerSource]

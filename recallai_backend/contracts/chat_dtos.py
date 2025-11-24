from pydantic import BaseModel
from typing import List, Optional


class ChatRequestDTO(BaseModel):
    conversation_id: int | None = None
    prompt: str
    top_k: int = 5


class ChatAnswerSource(BaseModel):
    note_id: int
    title: Optional[str]
    snippet: str


class ChatAttachmentDTO(BaseModel):
    filename: str
    content_type: Optional[str] = None
    size: Optional[int] = None


class ChatResponseDTO(BaseModel):
    answer: str
    sources: List[ChatAnswerSource] = []
    attachments: List[ChatAttachmentDTO] = []


class DeleteMessageDTO(BaseModel):
    message_id: int

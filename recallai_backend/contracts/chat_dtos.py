from typing import List, Optional
from pydantic import BaseModel


class ChatRequestDTO(BaseModel):
    user_id: Optional[int] = None               # OPTIONAL because old system allowed missing
    conversation_id: int | None = None
    prompt: str                                 # BACK TO ORIGINAL FIELD
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
    message_id: Optional[int] = None


class DeleteMessageDTO(BaseModel):
    message_id: int

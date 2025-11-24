"""
Conversation-related DTOs (contracts).

Moved from inline conversation_controller DTO classes into a proper
contracts file to maintain clean separation of concerns and match
the KaiHelper-style DTO structure.
"""

from pydantic import BaseModel


class UserID(BaseModel):
    user_id: int


class CreateConvDTO(BaseModel):
    user_id: int


class ConvID(BaseModel):
    conversation_id: int


class RenameDTO(BaseModel):
    conversation_id: int
    title: str


class DeleteDTO(BaseModel):
    conversation_id: int


class DeleteMessageDTO(BaseModel):
    message_id: int


class AddToNoteDTO(BaseModel):
    user_id: int
    content: str
    title: str | None = "Chat Snippet"


__all__ = [
    "UserID",
    "CreateConvDTO",
    "ConvID",
    "RenameDTO",
    "DeleteDTO",
    "DeleteMessageDTO",
    "AddToNoteDTO",
]

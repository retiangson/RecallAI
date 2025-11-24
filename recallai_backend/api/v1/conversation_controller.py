from fastapi import APIRouter

from recallai_backend.bootstrap import container
from recallai_backend.contracts.conversation_dtos import (
    UserID,
    CreateConvDTO,
    ConvID,
    RenameDTO,
    DeleteDTO,
    DeleteMessageDTO,
    AddToNoteDTO,
)

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.post("/list")
def list_conversations(dto: UserID):
    service = container.get_conversation_service()
    return service.list_for_user(dto.user_id)


@router.post("/create")
def create_conversation(dto: CreateConvDTO):
    service = container.get_conversation_service()
    return service.create(dto.user_id)


@router.post("/messages")
def get_messages(dto: ConvID, limit: int = 10, before_id: int | None = None):
    service = container.get_conversation_service()
    return service.get_messages_paginated(dto.conversation_id, limit, before_id)


@router.post("/rename")
def rename_conversation(dto: RenameDTO):
    service = container.get_conversation_service()
    return service.rename(dto.conversation_id, dto.title)


@router.post("/delete")
def delete_conversation(dto: DeleteDTO):
    service = container.get_conversation_service()
    return service.delete(dto.conversation_id)


@router.post("/delete-message")
def delete_message(dto: DeleteMessageDTO):
    service = container.get_conversation_service()
    return service.delete_message(dto.message_id)


@router.post("/add-to-note")
def add_to_note(dto: AddToNoteDTO):
    service = container.get_conversation_service()
    return service.add_message_to_note(dto.user_id, dto.content, dto.title)

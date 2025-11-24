from fastapi import APIRouter, Depends

from recallai_backend.di.request_container import (
    RequestContainer,
    get_request_container,
)
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
def list_conversations(
    dto: UserID,
    c: RequestContainer = Depends(get_request_container),
):
    return c.conversations().list_for_user(dto.user_id)


@router.post("/create")
def create_conversation(
    dto: CreateConvDTO,
    c: RequestContainer = Depends(get_request_container),
):
    return c.conversations().create(dto.user_id)


@router.post("/messages")
def get_messages(
    dto: ConvID,
    limit: int = 10,
    before_id: int | None = None,
    c: RequestContainer = Depends(get_request_container),
):
    return c.conversations().get_messages_paginated(dto.conversation_id, limit, before_id)


@router.post("/rename")
def rename_conversation(
    dto: RenameDTO,
    c: RequestContainer = Depends(get_request_container),
):
    return c.conversations().rename(dto.conversation_id, dto.title)


@router.post("/delete")
def delete_conversation(
    dto: DeleteDTO,
    c: RequestContainer = Depends(get_request_container),
):
    return c.conversations().delete(dto.conversation_id)


@router.post("/delete-message")
def delete_message(
    dto: DeleteMessageDTO,
    c: RequestContainer = Depends(get_request_container),
):
    return c.conversations().delete_message(dto.message_id)


@router.post("/add-to-note")
def add_to_note(
    dto: AddToNoteDTO,
    c: RequestContainer = Depends(get_request_container),
):
    return c.conversations().add_message_to_note(dto.user_id, dto.content, dto.title)

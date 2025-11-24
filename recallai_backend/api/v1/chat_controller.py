from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List

from recallai_backend.di.request_container import (
    RequestContainer,
    get_request_container,
)
from recallai_backend.contracts.chat_dtos import ChatRequestDTO, ChatResponseDTO

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponseDTO)
def ask_chat(
    dto: ChatRequestDTO,
    c: RequestContainer = Depends(get_request_container)
):
    service = c.chat()
    return service.ask(dto)


@router.post("/upload", response_model=ChatResponseDTO)
async def upload_chat(
    conversation_id: int = Form(...),
    prompt: str = Form(""),
    files: List[UploadFile] = File(...),
    c: RequestContainer = Depends(get_request_container),
):
    service = c.chat()
    return await service.handle_file_upload(conversation_id, prompt, files)

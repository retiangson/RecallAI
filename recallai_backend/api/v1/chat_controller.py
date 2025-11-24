from fastapi import APIRouter, UploadFile, File, Form
from typing import List

from recallai_backend.bootstrap import container
from recallai_backend.contracts.chat_dtos import ChatRequestDTO, ChatResponseDTO

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponseDTO)
def ask_chat(dto: ChatRequestDTO):
    service = container.get_chat_service()
    return service.ask(dto)


@router.post("/upload", response_model=ChatResponseDTO)
async def upload_chat(
    conversation_id: int = Form(...),
    prompt: str = Form(""),
    files: List[UploadFile] = File(...)
):
    service = container.get_chat_service()
    return await service.handle_file_upload(conversation_id, prompt, files)

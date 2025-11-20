from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from recallai_backend.core.dependencies import get_db, get_embedding_service
from recallai_backend.dtos.chat_dtos import ChatRequestDTO, ChatResponseDTO
from recallai_backend.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponseDTO)
def ask(
    dto: ChatRequestDTO,
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service),
):
        service = ChatService(db, emb)
        return service.ask(dto)


@router.post("/upload", response_model=ChatResponseDTO)
async def chat_upload(
    conversation_id: int = Form(...),
    prompt: str = Form(""),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service),
):
    """
    Multi-file upload + message in a single request.

    Frontend should send FormData like:
      formData.append("conversation_id", convId.toString());
      formData.append("prompt", text);
      formData.append("files", file1);
      formData.append("files", file2);
      ...
    """
    service = ChatService(db, emb)
    return await service.handle_file_upload(conversation_id, prompt, files)

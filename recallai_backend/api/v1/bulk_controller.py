from typing import List
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from openai import OpenAI
import mimetypes
import base64

from recallai_backend.core.dependencies import get_db, get_embedding_service
from recallai_backend.services.note_service import NoteService
from recallai_backend.utils.file_extractor import extract_text_local
from recallai_backend.dtos.note_dtos import NoteCreateDTO, NoteResponseDTO

router = APIRouter(prefix="/notes", tags=["notes"])
client = OpenAI()

IMAGE_EXTS = ["png", "jpg", "jpeg", "gif", "webp"]


def is_image(filename: str, content_type: str) -> bool:
    ext = filename.lower().split(".")[-1]
    return ext in IMAGE_EXTS or (content_type and content_type.startswith("image/"))


@router.post("/bulk", response_model=List[NoteResponseDTO])
async def upload_bulk_notes(
    user_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    service = NoteService(db)
    saved_notes = []

    for file in files:
        filename = file.filename or "file"
        mime = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        file_bytes = await file.read()

        # --------------------------------------------------
        # CASE 1 — IMAGE FILES → use GPT-4o Vision
        # --------------------------------------------------
        if is_image(filename, mime):
            b64 = base64.b64encode(file_bytes).decode()
            image_url = f"data:{mime};base64,{b64}"

            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Extract text from this image. Output raw text. No summary."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_image", "image_url": image_url}
                        ],
                    },
                ],
            )

            extracted_text = completion.choices[0].message.content

        # --------------------------------------------------
        # CASE 2 — ALL OTHER FILE TYPES → Local extraction only
        # --------------------------------------------------
        else:
            extracted_text = extract_text_local(file_bytes, filename)

        # --------------------------------------------------
        # SAVE NOTE
        # --------------------------------------------------
        if extracted_text and extracted_text.strip():
            saved_notes.append(
                service.create_note(
                    NoteCreateDTO(
                        user_id=user_id,
                        title=filename,
                        content=extracted_text,
                        source="bulk_upload",
                    )
                )
            )

    return saved_notes

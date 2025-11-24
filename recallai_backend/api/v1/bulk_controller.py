from typing import List
from fastapi import APIRouter, UploadFile, File
from openai import OpenAI
import base64, mimetypes

from recallai_backend.bootstrap import container
from recallai_backend.utils.file_extractor import extract_text_local
from recallai_backend.contracts.note_dtos import NoteCreateDTO, NoteResponseDTO

router = APIRouter(prefix="/notes", tags=["notes"])
client = OpenAI()

IMAGE_EXTS = ["png", "jpg", "jpeg", "gif", "webp"]


def is_image(filename: str, content_type: str) -> bool:
    ext = filename.lower().split(".")[-1]
    return ext in IMAGE_EXTS or (content_type and content_type.startswith("image/"))


@router.post("/bulk", response_model=List[NoteResponseDTO])
async def upload_bulk_notes(user_id: int, files: List[UploadFile] = File(...)):
    service = container.get_note_service()
    saved_notes: List[NoteResponseDTO] = []

    for file in files:
        filename = file.filename or "file"
        mime = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        file_bytes = await file.read()

        if is_image(filename, mime):
            b64 = base64.b64encode(file_bytes).decode()
            image_url = f"data:{mime};base64,{b64}"

            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Extract text from this image. Output raw text."},
                    {"role": "user", "content": [{"type": "input_image", "image_url": image_url}]},
                ],
            )
            extracted_text = completion.choices[0].message.content
        else:
            extracted_text = extract_text_local(file_bytes, filename)

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

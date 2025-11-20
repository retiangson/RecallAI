from typing import List

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from openai import OpenAI
import mimetypes
import base64

from app.core.dependencies import get_db, get_embedding_service
from app.services.note_service import NoteService
from app.utils.file_extractor import extract_text_gpt
from app.dtos.note_dtos import NoteCreateDTO, NoteResponseDTO

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
    emb = Depends(get_embedding_service),
):
    service = NoteService(db, emb)
    saved_notes = []

    for file in files:
        filename = file.filename or "file"
        mime = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        file_bytes = await file.read()

        # ---------------------------------------------------------
        # CASE 1 — IMAGE → base64 → image_url (correct schema)
        # ---------------------------------------------------------
        if is_image(filename, mime):
            b64 = base64.b64encode(file_bytes).decode()
            image_url = f"data:{mime};base64,{b64}"

            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract all visible text and convert to markdown notes."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ]
            )

            extracted_notes = completion.choices[0].message.content

        # ----------------------------------------------------
        # CASE 2: PDF → upload & use type="file"
        # ----------------------------------------------------
        elif filename.lower().endswith(".pdf"):
            uploaded = client.files.create(
                file=(filename, file_bytes, mime),
                purpose="vision"   # allowed only for PDF
            )

            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract and summarize text from this PDF into clean markdown."
                    },
                    {
                        "role": "user",
                        "content": [
                            { "type": "file", "file": { "file_id": uploaded.id } }
                        ]
                    }
                ]
            )

            extracted_notes = completion.choices[0].message.content

        # ----------------------------------------------------
        # CASE 3: DOCX / PPTX / XLSX / TXT / ZIP → local extract
        # ----------------------------------------------------
        else:
            extracted_raw = extract_text_gpt(file_bytes, filename)

            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Convert raw extracted text into clean structured markdown notes."
                    },
                    {
                        "role": "user",
                        "content": [
                            { "type": "text", "text": extracted_raw }
                        ]
                    }
                ]
            )

            extracted_notes = completion.choices[0].message.content

        if extracted_notes.strip():
            saved_notes.append(
                service.create_note(
                    NoteCreateDTO(
                        user_id=user_id,
                        title=filename,
                        content=extracted_notes,
                        source="bulk_upload",
                    )
                )
            )

    return saved_notes

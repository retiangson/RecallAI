from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List
import io
import zipfile

from app.core.dependencies import get_db, get_embedding_service
from app.services.note_service import NoteService
from app.dtos.note_dtos import NoteResponseDTO

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/bulk", response_model=List[NoteResponseDTO])
async def upload_bulk_notes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    emb = Depends(get_embedding_service),
):
    """
    Accept multiple .txt files or a .zip file containing .txt files.
    Extracts text, embeds it, stores into RecallAI memory.
    """
    service = NoteService(db, emb)
    saved_notes = []

    for file in files:
        filename = file.filename.lower()

        # If ZIP file, extract all .txt
        if filename.endswith(".zip"):
            contents = await file.read()
            with zipfile.ZipFile(io.BytesIO(contents), "r") as zip_ref:
                for item_name in zip_ref.namelist():
                    if not item_name.lower().endswith(".txt"):
                        continue
                    text = zip_ref.read(item_name).decode("utf-8", errors="ignore")
                    dto = {
                        "title": item_name.replace(".txt", ""),
                        "content": text,
                        "source": file.filename,
                    }
                    note = service.create_note(dto)
                    saved_notes.append(note)

        # Handle regular .txt files
        elif filename.endswith(".txt"):
            text = (await file.read()).decode("utf-8", errors="ignore")
            dto = {
                "title": file.filename.replace(".txt", ""),
                "content": text,
                "source": file.filename,
            }
            note = service.create_note(dto)
            saved_notes.append(note)

        else:
            # Ignore other file types
            continue

    return saved_notes

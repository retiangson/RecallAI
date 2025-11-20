import docx
import PyPDF2
import zipfile
import io
from typing import List
from openai import OpenAI

client = OpenAI()

def extract_text_local(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1]

    # ----- PDF -----
    if ext == "pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    # ----- DOCX -----
    if ext == "docx":
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    # ----- TXT -----
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")

    # ----- ZIP -----
    if ext == "zip":
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            out = []
            for name in z.namelist():
                if name.lower().endswith(".txt"):
                    out.append(z.read(name).decode("utf-8", errors="ignore"))
        return "\n".join(out)

    return "Unable to extract text locally."


def extract_text_gpt(file_bytes_list: List[bytes], filenames: List[str]) -> str:
    """Local extraction first → GPT cleaning second."""

    # 1) Local raw extraction
    raw_text = extract_text_local(file_bytes_list[0], filenames[0])

    # 2) GPT cleaning pass
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Clean and normalize this extracted text:\n\n{raw_text}"}
                ]
            }
        ]
    )

    return completion.choices[0].message.content

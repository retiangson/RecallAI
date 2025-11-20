from typing import List
from openai import OpenAI

client = OpenAI()

async def extract_text_gpt(file_bytes_list: List[bytes], filenames: List[str]) -> str:
    """
    Universal extractor using GPT-4o Vision.
    Works for ALL file types: PDF, DOCX, PPT, XLSX, IMAGES, TXT, etc.
    """

    # Upload all files to OpenAI
    file_ids = []
    for bytes_, name in zip(file_bytes_list, filenames):
        uploaded = client.files.create(
            file=(name, bytes_, "application/octet-stream"),
            purpose="vision"
        )
        file_ids.append(uploaded.id)

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract ALL text from these files."},
                *[
                    {"type": "file", "file": {"file_id": f}}
                    for f in file_ids
                ]
            ]
        }]
    )

    return completion.choices[0].message["content"]

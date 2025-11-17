from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)


class EmbeddingService:
    def __init__(self, model: str | None = None):
        self.model = model or settings.openai_embedding_model

    def embed_text(self, text: str) -> list[float]:
        resp = client.embeddings.create(
            model=self.model,
            input=text
        )
        return resp.data[0].embedding

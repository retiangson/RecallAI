from pydantic_settings import BaseSettings
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env manually using absolute path
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BACKEND_ROOT / ".env"
load_dotenv(ENV_PATH)
print("DEBUG ENV PATH LOADED:", ENV_PATH)

class Settings(BaseSettings):
    app_name: str = "RecallAI - Personal Notes Assistant"

    # Database (Supabase Postgres)
    database_url: str

    # OpenAI config
    openai_api_key: str
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"


settings = Settings()

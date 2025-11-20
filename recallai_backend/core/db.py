# app/core/db.py

from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from recallai_backend.core.config import settings


# SQLAlchemy 2.0 style Base class
class Base(DeclarativeBase):
    pass


# Create engine
engine = create_engine(
    settings.database_url,
    echo=False,
    future=True
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

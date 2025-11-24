# recallai_backend/core/db.py

from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import create_engine
from recallai_backend.core.config import settings


# -----------------------------------------------------
# SQLAlchemy Base (2.0 style)
# -----------------------------------------------------
class Base(DeclarativeBase):
    pass


# -----------------------------------------------------
# Engine (AWS-safe, connection-stable)
# -----------------------------------------------------
engine = create_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,        # prevents "MySQL server has gone away"
)


# -----------------------------------------------------
# Session Factory (NOT a session instance!)
# -----------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,    # do not expire objects after commit
    future=True,
)


# -----------------------------------------------------
# FastAPI Dependency (Transient per-request session)
# -----------------------------------------------------
def get_db() -> Session:
    """
    Provides a NEW SQLAlchemy session for each incoming
    request. Ensures the session is closed after request,
    preventing concurrency issues and session leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

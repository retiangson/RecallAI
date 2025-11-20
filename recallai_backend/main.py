import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Allow Lambda stage prefix (e.g. /Prod)
STAGE_BASE = os.getenv("STAGE_BASE", "").rstrip("/")  # "" locally, "/Prod" in AWS

BACKEND_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_ROOT)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from recallai_backend.core.db import Base, engine
from recallai_backend.api.v1 import (
    notes_controller,
    chat_controller,
    bulk_controller,
    auth_controller,
    conversation_controller
)

# ----------------------------
# FASTAPI with stage support
# ----------------------------
app = FastAPI(
    title="RecallAI - Personal Notes Assistant",
    version="1.0.0",
    docs_url="/api/docs",              # <--- FIXED
    openapi_url="/api/openapi.json",   # <--- FIXED
    redoc_url="/api/redoc",
    root_path=STAGE_BASE or "",        # <--- FIXED
)

@app.get("/health", tags=["system"])
def healthcheck():
    return {"status": "ok"}

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# ROUTES (under /api/*)
# ----------------------------
app.include_router(auth_controller.router, prefix="/api")
app.include_router(notes_controller.router, prefix="/api")
app.include_router(chat_controller.router, prefix="/api")
app.include_router(bulk_controller.router, prefix="/api")
app.include_router(conversation_controller.router, prefix="/api")

# Lambda handler
handler = Mangum(app)

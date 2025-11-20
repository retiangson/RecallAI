import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# -------------------------------------
# CREATE APP
# -------------------------------------
app = FastAPI(title="RecallAI - Personal Notes Assistant")

# -------------------------------------
# GLOBAL HEALTHCHECK (Best Practice)
# -------------------------------------
@app.get("/health", tags=["system"])
def healthcheck():
    return {
        "status": "ok",
        "service": "recallai-backend",
        "version": "1.0.0",
        "environment": "lambda",
    }

# -------------------------------------
# CORS CONFIG
# -------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------
# ROUTERS
# -------------------------------------
app.include_router(auth_controller.router, prefix="/api/v1")
app.include_router(notes_controller.router, prefix="/api/v1")
app.include_router(chat_controller.router, prefix="/api/v1")
app.include_router(bulk_controller.router, prefix="/api/v1")
app.include_router(conversation_controller.router, prefix="/api/v1")

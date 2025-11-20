import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("DEBUG: app/main.py executing")
# -------------------------------------
# FIX PYTHONPATH for Lambda
# -------------------------------------
BACKEND_ROOT = os.path.dirname(os.path.abspath(__file__))  # recallai_backend/app
PROJECT_ROOT = os.path.dirname(BACKEND_ROOT)               # recallai_backend

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------------------
# IMPORTS (after sys.path fix)
# -------------------------------------
from app.core.db import Base, engine
from app.api.v1 import (
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
# DO NOT RUN MIGRATIONS ON IMPORT
# -------------------------------------
# Base.metadata.create_all(bind=engine)
# (This must NOT run in Lambda cold start)

# -------------------------------------
# ROUTERS
# -------------------------------------
app.include_router(auth_controller.router, prefix="/api/v1")
app.include_router(notes_controller.router, prefix="/api/v1")
app.include_router(chat_controller.router, prefix="/api/v1")
app.include_router(bulk_controller.router, prefix="/api/v1")
app.include_router(conversation_controller.router, prefix="/api/v1")

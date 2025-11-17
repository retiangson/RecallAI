import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# -------------------------------------
# FIX PYTHONPATH so "app" is importable
# -------------------------------------
BACKEND_ROOT = os.path.dirname(os.path.abspath(__file__))  # recallai_backend/app
PROJECT_ROOT = os.path.dirname(BACKEND_ROOT)               # recallai_backend

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print("DEBUG: sys.path[0] =", sys.path[0])
print("DEBUG: cwd =", os.getcwd())

# -------------------------------------
# IMPORTS (after sys.path fix)
# -------------------------------------
from app.core.db import Base, engine
from app.api.v1 import notes_controller, chat_controller, bulk_controller

# -------------------------------------
# CREATE APP
# -------------------------------------
app = FastAPI(title="RecallAI - Personal Notes Assistant")

# -------------------------------------
# CORS CONFIG
# -------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev: allow everything (React, localhost)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------
# CREATE TABLES
# -------------------------------------
Base.metadata.create_all(bind=engine)

# -------------------------------------
# ROUTERS
# -------------------------------------
app.include_router(notes_controller.router, prefix="/api/v1")
app.include_router(chat_controller.router, prefix="/api/v1")
app.include_router(bulk_controller.router, prefix="/api/v1")

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# 1) Same behavior as KaiHelper
STAGE_BASE = os.getenv("STAGE_BASE", "").rstrip("/")  # "/Prod" on Lambda

BACKEND_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# IMPORT ROUTERS
from recallai_backend.core.db import Base, engine
from recallai_backend.api.v1 import (
    notes_controller,
    chat_controller,
    bulk_controller,
    auth_controller,
    conversation_controller,
)

# 2) Same FastAPI initializer as KaiHelper
app = FastAPI(
    title="RecallAI - Personal Notes Assistant",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
    root_path=STAGE_BASE or "",
)

# 3) HEALTH CHECK
@app.get("/health")
def health():
    return {"status": "ok", "stage": STAGE_BASE}

# 4) CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5) ROUTERS placed under /api (same as KaiHelper)
app.include_router(auth_controller.router, prefix="/api")
app.include_router(notes_controller.router, prefix="/api")
app.include_router(chat_controller.router, prefix="/api")
app.include_router(bulk_controller.router, prefix="/api")
app.include_router(conversation_controller.router, prefix="/api")

# 6) LAMBDA HANDLER
handler = Mangum(app)

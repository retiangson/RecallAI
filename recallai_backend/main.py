import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from fastapi.openapi.utils import get_openapi

# -----------------------------------------------------
# 1) Stage prefix (IMPORTANT for API Gateway /Prod)
# -----------------------------------------------------
STAGE_BASE = os.getenv("STAGE_BASE", "").rstrip("/")  # "/Prod" in Lambda

# -----------------------------------------------------
# 2) Fix Python paths so recallai_backend imports work
# -----------------------------------------------------
BACKEND_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -----------------------------------------------------
# 3) Import Routers & DB
# -----------------------------------------------------
from recallai_backend.core.db import Base, engine
from recallai_backend.api.v1 import (
    notes_controller,
    chat_controller,
    bulk_controller,
    auth_controller,
    conversation_controller,
)

# -----------------------------------------------------
# 4) FastAPI app (MATCHED to KaiHelper)
# -----------------------------------------------------
app = FastAPI(
    title="RecallAI - Personal Notes Assistant",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
    root_path=STAGE_BASE or "",
)

# -----------------------------------------------------
# 5) Custom OpenAPI (CRITICAL FIX for 403 errors)
# -----------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    # Add servers section so Swagger uses /Prod/api/*
    if STAGE_BASE:
        schema["servers"] = [{"url": STAGE_BASE}]  # e.g. "/Prod"

    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi


# -----------------------------------------------------
# 6) Healthcheck
# -----------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "stage": STAGE_BASE}


# -----------------------------------------------------
# 7) CORS
# -----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------
# 8) ROUTERS (all under /api, matching docs paths)
# -----------------------------------------------------
app.include_router(auth_controller.router, prefix="/api")
app.include_router(notes_controller.router, prefix="/api")
app.include_router(chat_controller.router, prefix="/api")
app.include_router(bulk_controller.router, prefix="/api")
app.include_router(conversation_controller.router, prefix="/api")


# -----------------------------------------------------
# 9) Lambda handler
# -----------------------------------------------------
handler = Mangum(app)

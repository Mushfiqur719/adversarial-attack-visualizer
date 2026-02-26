"""FastAPI application entry point."""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import attacks, datasets, metrics, models, sandbox
from app.ws.attack_ws import attack_websocket_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── App Setup ──────────────────────────────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Research platform for designing, testing, and benchmarking adversarial attack algorithms.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──────────────────────────────────────────────────────────

app.include_router(attacks.router)
app.include_router(datasets.router)
app.include_router(models.router)
app.include_router(metrics.router)
app.include_router(sandbox.router)

# ── WebSocket ──────────────────────────────────────────────────────────────────

app.websocket("/ws/attack")(attack_websocket_handler)


# ── Events ─────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    """Create required directories on startup."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    logger.info("🚀 %s v%s started", settings.APP_TITLE, settings.APP_VERSION)
    logger.info("   Device: %s", settings.DEVICE)


@app.get("/")
async def root():
    return {
        "name": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    import torch
    return {
        "status": "ok",
        "cuda_available": torch.cuda.is_available(),
        "device": settings.DEVICE,
    }

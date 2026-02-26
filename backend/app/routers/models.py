"""API routes for model operations."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.schemas import ModelName
from app.services.model_service import get_model_info, list_models

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("/")
async def list_all_models():
    """List all available models."""
    return list_models()


@router.get("/{name}")
async def get_model(name: ModelName):
    """Get info about a specific model."""
    return get_model_info(name)

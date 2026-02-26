"""API routes for dataset operations."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.schemas import DatasetName
from app.services.dataset_service import (
    get_dataset_info,
    get_sample,
    list_datasets,
)
from app.core.summary_writer import numpy_to_base64

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("/")
async def list_all_datasets():
    """List all available datasets with metadata."""
    return list_datasets()


@router.get("/{name}")
async def get_dataset(name: DatasetName):
    """Get info and sample images for a specific dataset."""
    return get_dataset_info(name)


@router.get("/{name}/sample/{index}")
async def get_dataset_sample(name: DatasetName, index: int):
    """Get a single sample from a dataset."""
    image, label = get_sample(name, index)
    return {
        "index": index,
        "label": int(label),
        "image_base64": numpy_to_base64(image),
    }

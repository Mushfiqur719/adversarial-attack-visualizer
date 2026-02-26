"""API routes for metrics computation."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.schemas import MetricsResult

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/")
async def metrics_info():
    """List available metrics and their descriptions."""
    return {
        "metrics": [
            {"name": "l0_norm", "unit": "pixels", "description": "Number of pixels modified"},
            {"name": "l2_norm", "unit": "euclidean", "description": "Euclidean distance between original and adversarial"},
            {"name": "linf_norm", "unit": "max_change", "description": "Maximum pixel change (L-infinity norm)"},
            {"name": "psnr", "unit": "dB", "description": "Peak Signal-to-Noise Ratio (higher = less distortion)"},
            {"name": "ssim", "unit": "0-1", "description": "Structural Similarity Index (1.0 = identical)"},
            {"name": "success_rate", "unit": "%", "description": "Attack success rate"},
        ]
    }

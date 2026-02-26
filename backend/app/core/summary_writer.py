"""Custom ART SummaryWriter for capturing intermediate attack frames."""

from __future__ import annotations

import base64
import io
import logging
from typing import Any

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class FrameCaptureSummaryWriter:
    """
    Captures per-iteration data from ART attacks for real-time streaming.
    
    Stores intermediate perturbed images, loss values, gradient norms,
    and predictions so they can be streamed via WebSocket.
    """

    def __init__(self):
        self.frames: list[dict[str, Any]] = []
        self._current_iteration = 0

    def reset(self):
        self.frames = []
        self._current_iteration = 0

    def update(self, batch_id: int, global_step: int, grad: Any = None,
               patch: Any = None, estimator: Any = None, x: Any = None,
               y: Any = None, **kwargs):
        """Called by ART attacks at each iteration."""
        frame: dict[str, Any] = {
            "iteration": global_step,
            "batch_id": batch_id,
        }

        # Capture gradient norm if available
        if grad is not None:
            try:
                grad_np = np.array(grad)
                frame["gradient_norm"] = float(np.linalg.norm(grad_np))
            except Exception:
                pass

        # Capture loss if passed in kwargs
        if "loss" in kwargs:
            frame["loss"] = float(kwargs["loss"])

        # Capture intermediate perturbed image
        if x is not None:
            try:
                frame["image_base64"] = self._array_to_base64(x[0] if len(x.shape) == 4 else x)
            except Exception:
                pass

        # Capture predictions if estimator available
        if estimator is not None and x is not None:
            try:
                preds = estimator.predict(x[:1])
                pred_label = int(np.argmax(preds[0]))
                pred_conf = float(np.max(preds[0]))
                frame["prediction"] = {
                    "label": pred_label,
                    "confidence": pred_conf,
                    "probabilities": preds[0].tolist(),
                }
            except Exception:
                pass

        self.frames.append(frame)
        self._current_iteration = global_step

    @staticmethod
    def _array_to_base64(img_array: np.ndarray) -> str:
        """Convert a numpy image array to base64 PNG string."""
        img = img_array.copy()

        # Handle channel dimension
        if img.ndim == 3 and img.shape[0] in (1, 3):
            img = np.transpose(img, (1, 2, 0))

        # Squeeze single-channel
        if img.ndim == 3 and img.shape[2] == 1:
            img = img.squeeze(2)

        # Normalize to 0-255
        if img.max() <= 1.0:
            img = (img * 255).astype(np.uint8)
        else:
            img = img.astype(np.uint8)

        pil_img = Image.fromarray(img)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def get_frames(self) -> list[dict[str, Any]]:
        return self.frames


def numpy_to_base64(img_array: np.ndarray) -> str:
    """Utility: convert numpy image to base64 PNG."""
    return FrameCaptureSummaryWriter._array_to_base64(img_array)

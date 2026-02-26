"""Sandbox execution service — runs user-defined attack code in-process."""

from __future__ import annotations

import io
import logging
import signal
import sys
import threading
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Any

import numpy as np

from app.config import get_settings

logger = logging.getLogger(__name__)


class SandboxTimeout(Exception):
    pass


class IterationReporter:
    """
    Callback object injected into user code.
    Users call `report_iteration(...)` to stream intermediate results.
    """

    def __init__(self):
        self.frames: list[dict[str, Any]] = []

    def report_iteration(self, iteration: int, image: np.ndarray = None,
                         loss: float = None, metrics: dict = None,
                         prediction: dict = None, **kwargs):
        """
        Report an intermediate iteration result.

        Args:
            iteration: Current iteration number
            image: Perturbed image as numpy array (C,H,W) or (H,W,C)
            loss: Current loss value
            metrics: Dict of custom metrics
            prediction: Dict with 'label' and 'confidence'
            **kwargs: Any additional data to include
        """
        from app.core.summary_writer import numpy_to_base64

        frame = {"iteration": iteration}

        if image is not None:
            frame["image_base64"] = numpy_to_base64(image)

        if loss is not None:
            frame["loss"] = float(loss)

        if metrics:
            frame["metrics"] = {k: float(v) for k, v in metrics.items()}

        if prediction:
            frame["prediction"] = prediction

        frame.update(kwargs)
        self.frames.append(frame)


def execute_code(code: str, context: dict[str, Any] = None,
                 timeout: int = None) -> dict[str, Any]:
    """
    Execute user-provided Python code in a restricted environment.

    Args:
        code: Python source code string
        context: Variables to inject (model, dataset, params, etc.)
        timeout: Max execution time in seconds

    Returns:
        Dict with success, stdout, stderr, frames, result, elapsed_seconds
    """
    if timeout is None:
        timeout = get_settings().SANDBOX_TIMEOUT

    reporter = IterationReporter()

    # Build restricted global namespace
    allowed_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "min": min,
            "max": max,
            "abs": abs,
            "sum": sum,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "sorted": sorted,
            "isinstance": isinstance,
            "type": type,
            "hasattr": hasattr,
            "getattr": getattr,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "RuntimeError": RuntimeError,
            "Exception": Exception,
        },
        "np": np,
        "numpy": np,
        "report_iteration": reporter.report_iteration,
    }

    # Import ML libraries
    try:
        import torch
        allowed_globals["torch"] = torch
    except ImportError:
        pass

    try:
        import torchvision
        allowed_globals["torchvision"] = torchvision
    except ImportError:
        pass

    try:
        from PIL import Image
        allowed_globals["Image"] = Image
    except ImportError:
        pass

    try:
        import art
        allowed_globals["art"] = art
    except ImportError:
        pass

    # Inject user context (model, image, label, etc.)
    if context:
        allowed_globals.update(context)

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    result = {
        "success": False,
        "stdout": "",
        "stderr": "",
        "frames": [],
        "result": None,
        "elapsed_seconds": 0.0,
    }

    exec_result = {}

    def _run():
        try:
            exec(code, allowed_globals, exec_result)
        except Exception as e:
            exec_result["__error__"] = traceback.format_exc()

    start_time = time.time()

    with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=timeout)

    elapsed = time.time() - start_time
    result["elapsed_seconds"] = round(elapsed, 3)
    result["stdout"] = stdout_buf.getvalue()
    result["stderr"] = stderr_buf.getvalue()
    result["frames"] = reporter.frames

    if thread.is_alive():
        result["stderr"] += f"\n[TIMEOUT] Execution exceeded {timeout}s limit."
        result["success"] = False
    elif "__error__" in exec_result:
        result["stderr"] += exec_result["__error__"]
        result["success"] = False
    else:
        result["success"] = True
        # Capture any 'result' variable set by user code
        if "result" in exec_result:
            result["result"] = exec_result["result"]
        elif "adversarial_image" in exec_result:
            result["result"] = exec_result["adversarial_image"]

    return result

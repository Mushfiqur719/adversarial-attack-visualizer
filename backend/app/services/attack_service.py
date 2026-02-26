"""Attack orchestration service — built-in ART attacks + custom attack execution."""

from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np

from app.core.schemas import (
    AttackConfig, AttackFrame, AttackInfo, AttackResult, AttackType,
    CustomAttackRequest, ParamDef,
)
from app.core.summary_writer import FrameCaptureSummaryWriter, numpy_to_base64
from app.services.dataset_service import get_sample
from app.services.metrics_service import compute_all_metrics
from app.services.model_service import load_model
from app.services.sandbox_service import execute_code

logger = logging.getLogger(__name__)


# ── Attack Registry ────────────────────────────────────────────────────────────

ATTACK_REGISTRY: list[AttackInfo] = [
    AttackInfo(
        name="fgsm", display_name="FGSM (Fast Gradient Sign Method)",
        type=AttackType.FGSM,
        description="One-step gradient attack: perturbs each pixel in the direction of the loss gradient sign.",
        is_iterative=False,
        params=[
            ParamDef(name="eps", label="Epsilon (ε)", type="float",
                     min=0.0, max=1.0, step=0.01, default=0.3),
            ParamDef(name="eps_step", label="Step Size", type="float",
                     min=0.001, max=0.5, step=0.001, default=0.1),
            ParamDef(name="targeted", label="Targeted Attack", type="bool",
                     default=False),
        ],
    ),
    AttackInfo(
        name="pgd", display_name="PGD (Projected Gradient Descent)",
        type=AttackType.PGD,
        description="Iterative gradient attack with projection onto Lp ball. Multi-step refinement of FGSM.",
        is_iterative=True,
        params=[
            ParamDef(name="eps", label="Epsilon (ε)", type="float",
                     min=0.0, max=1.0, step=0.01, default=0.3),
            ParamDef(name="eps_step", label="Step Size (α)", type="float",
                     min=0.001, max=0.5, step=0.001, default=0.01),
            ParamDef(name="max_iter", label="Max Iterations", type="int",
                     min=1, max=200, step=1, default=40),
            ParamDef(name="targeted", label="Targeted Attack", type="bool",
                     default=False),
        ],
    ),
    AttackInfo(
        name="cw", display_name="C&W (Carlini & Wagner L2)",
        type=AttackType.CW,
        description="Optimization-based attack minimizing L2 perturbation to cross decision boundary.",
        is_iterative=True,
        params=[
            ParamDef(name="confidence", label="Confidence (κ)", type="float",
                     min=0.0, max=50.0, step=0.5, default=0.0),
            ParamDef(name="learning_rate", label="Learning Rate", type="float",
                     min=0.0001, max=0.1, step=0.0001, default=0.01),
            ParamDef(name="max_iter", label="Max Iterations", type="int",
                     min=1, max=200, step=1, default=50),
            ParamDef(name="binary_search_steps", label="Binary Search Steps", type="int",
                     min=1, max=20, step=1, default=5),
        ],
    ),
    AttackInfo(
        name="deepfool", display_name="DeepFool",
        type=AttackType.DEEPFOOL,
        description="Geometric attack finding minimal perturbation to nearest decision boundary.",
        is_iterative=True,
        params=[
            ParamDef(name="max_iter", label="Max Iterations", type="int",
                     min=1, max=200, step=1, default=50),
            ParamDef(name="epsilon", label="Overshoot (ε)", type="float",
                     min=0.0, max=1.0, step=0.001, default=1e-6),
        ],
    ),
    AttackInfo(
        name="square", display_name="Square Attack",
        type=AttackType.SQUARE,
        description="Black-box score-based attack using random square-shaped perturbations.",
        is_iterative=True,
        params=[
            ParamDef(name="max_iter", label="Max Queries", type="int",
                     min=100, max=10000, step=100, default=1000),
            ParamDef(name="eps", label="Epsilon (ε)", type="float",
                     min=0.0, max=1.0, step=0.01, default=0.3),
            ParamDef(name="p_init", label="Initial Perturbation %", type="float",
                     min=0.01, max=1.0, step=0.01, default=0.8),
        ],
    ),
]


def get_attack_registry() -> list[AttackInfo]:
    return ATTACK_REGISTRY


# ── Input Preprocessing ───────────────────────────────────────────────────────

def _adapt_input(x: np.ndarray, classifier) -> np.ndarray:
    """
    Adapt input image to match the model's expected input shape.
    Handles channel replication (1ch→3ch) and spatial resizing.
    """
    from PIL import Image as PILImage

    expected_shape = classifier.input_shape  # e.g. (3, 224, 224)
    expected_c, expected_h, expected_w = expected_shape
    _, actual_c, actual_h, actual_w = x.shape

    result = x.copy()

    # Channel adaptation: replicate 1ch grayscale → 3ch RGB
    if actual_c == 1 and expected_c == 3:
        result = np.repeat(result, 3, axis=1)
        actual_c = 3

    # Spatial resize if needed
    if actual_h != expected_h or actual_w != expected_w:
        resized = []
        for i in range(result.shape[0]):
            # (C, H, W) → (H, W, C) for PIL
            img = np.transpose(result[i], (1, 2, 0))
            if img.max() <= 1.0:
                img = (img * 255).astype(np.uint8)
            pil_img = PILImage.fromarray(img.squeeze() if actual_c == 1 else img)
            pil_img = pil_img.resize((expected_w, expected_h), PILImage.BILINEAR)
            arr = np.array(pil_img, dtype=np.float32) / 255.0
            if arr.ndim == 2:
                arr = arr[np.newaxis, ...]
            else:
                arr = np.transpose(arr, (2, 0, 1))
            resized.append(arr)
        result = np.array(resized, dtype=np.float32)

    return result


def _unadapt_output(x_adv_adapted: np.ndarray, original_x: np.ndarray) -> np.ndarray:
    """
    Convert adapted adversarial image back to original shape for metrics.
    """
    from PIL import Image as PILImage

    _, orig_c, orig_h, orig_w = original_x.shape
    _, adv_c, adv_h, adv_w = x_adv_adapted.shape

    result = x_adv_adapted.copy()

    # Spatial resize back if needed
    if adv_h != orig_h or adv_w != orig_w:
        resized = []
        for i in range(result.shape[0]):
            img = np.transpose(result[i], (1, 2, 0))
            if img.max() <= 1.0:
                img_uint8 = (img * 255).astype(np.uint8)
            else:
                img_uint8 = img.astype(np.uint8)
            pil_img = PILImage.fromarray(img_uint8.squeeze() if orig_c == 1 else img_uint8)
            pil_img = pil_img.resize((orig_w, orig_h), PILImage.BILINEAR)
            arr = np.array(pil_img, dtype=np.float32) / 255.0
            if arr.ndim == 2:
                arr = arr[np.newaxis, ...]
            else:
                arr = np.transpose(arr, (2, 0, 1))
            resized.append(arr)
        result = np.array(resized, dtype=np.float32)

    # Channel reduction: 3ch→1ch (average)
    if adv_c == 3 and orig_c == 1:
        result = np.mean(result, axis=1, keepdims=True)

    return result


# ── Built-in Attack Execution ──────────────────────────────────────────────────

def run_builtin_attack(config: AttackConfig) -> AttackResult:
    """Run a built-in ART attack with the given configuration."""
    start_time = time.time()

    # Load model and sample
    classifier, _ = load_model(config.model, config.dataset)
    image, true_label = get_sample(config.dataset, config.sample_index)
    x_original = image[np.newaxis, ...]  # (1, C, H, W) — original shape

    # Adapt input to model's expected shape (handles 1ch→3ch, resize)
    x = _adapt_input(x_original, classifier)

    # Get original prediction
    orig_preds = classifier.predict(x)[0]
    orig_label = int(np.argmax(orig_preds))
    orig_conf = float(np.max(orig_preds))

    # Create summary writer for frame capture
    writer = FrameCaptureSummaryWriter()

    # Run the attack
    attack = _create_art_attack(config, classifier, writer)

    if config.targeted and config.target_label is not None:
        y_target = np.zeros((1, classifier.nb_classes), dtype=np.float32)
        y_target[0, config.target_label] = 1.0
        x_adv = attack.generate(x=x, y=y_target)
    else:
        x_adv = attack.generate(x=x)

    # Get adversarial prediction
    adv_preds = classifier.predict(x_adv)[0]
    adv_label = int(np.argmax(adv_preds))
    adv_conf = float(np.max(adv_preds))

    # Convert adversarial back to original shape for metrics/display
    x_adv_display = _unadapt_output(x_adv, x_original)

    # Compute metrics on original-shaped images
    metrics = compute_all_metrics(
        x_original[0], x_adv_display[0], orig_preds, adv_preds, true_label
    )

    # Compute noise visualization
    noise = x_adv_display[0] - x_original[0]

    # Build frames from summary writer
    frames = []
    for f in writer.get_frames():
        frames.append(AttackFrame(
            iteration=f.get("iteration", 0),
            image_base64=f.get("image_base64", ""),
            prediction=f.get("prediction", {}),
            loss=f.get("loss"),
            gradient_norm=f.get("gradient_norm"),
            metrics=f.get("metrics", {}),
        ))

    # If no frames were captured, create start and end frames
    if not frames:
        frames = [
            AttackFrame(
                iteration=0,
                image_base64=numpy_to_base64(x_original[0]),
                prediction={"label": orig_label, "confidence": orig_conf},
            ),
            AttackFrame(
                iteration=1,
                image_base64=numpy_to_base64(x_adv_display[0]),
                prediction={"label": adv_label, "confidence": adv_conf},
                metrics=metrics,
            ),
        ]

    elapsed = time.time() - start_time

    return AttackResult(
        success=adv_label != true_label,
        original_label=orig_label,
        original_confidence=orig_conf,
        adversarial_label=adv_label,
        adversarial_confidence=adv_conf,
        original_image_base64=numpy_to_base64(x_original[0]),
        adversarial_image_base64=numpy_to_base64(x_adv_display[0]),
        noise_image_base64=numpy_to_base64(
            np.clip(noise * 10 + 0.5, 0, 1)  # amplified noise for visibility
        ),
        frames=frames,
        metrics=metrics,
        total_iterations=len(frames),
        elapsed_seconds=round(elapsed, 3),
    )


def _create_art_attack(config: AttackConfig, classifier, writer):
    """Instantiate an ART attack object based on the config."""
    params = config.params

    if config.attack_type == AttackType.FGSM:
        from art.attacks.evasion import FastGradientMethod
        return FastGradientMethod(
            estimator=classifier,
            eps=params.get("eps", 0.3),
            eps_step=params.get("eps_step", 0.1),
            targeted=config.targeted,
            summary_writer=writer,
        )
    elif config.attack_type == AttackType.PGD:
        from art.attacks.evasion import ProjectedGradientDescent
        return ProjectedGradientDescent(
            estimator=classifier,
            eps=params.get("eps", 0.3),
            eps_step=params.get("eps_step", 0.01),
            max_iter=params.get("max_iter", 40),
            targeted=config.targeted,
            summary_writer=writer,
        )
    elif config.attack_type == AttackType.CW:
        from art.attacks.evasion import CarliniL2Method
        return CarliniL2Method(
            classifier=classifier,
            confidence=params.get("confidence", 0.0),
            learning_rate=params.get("learning_rate", 0.01),
            max_iter=params.get("max_iter", 50),
            binary_search_steps=params.get("binary_search_steps", 5),
        )
    elif config.attack_type == AttackType.DEEPFOOL:
        from art.attacks.evasion import DeepFool
        return DeepFool(
            classifier=classifier,
            max_iter=params.get("max_iter", 50),
            epsilon=params.get("epsilon", 1e-6),
        )
    elif config.attack_type == AttackType.SQUARE:
        from art.attacks.evasion import SquareAttack
        return SquareAttack(
            estimator=classifier,
            max_iter=params.get("max_iter", 1000),
            eps=params.get("eps", 0.3),
            p_init=params.get("p_init", 0.8),
        )
    else:
        raise ValueError(f"Unknown attack type: {config.attack_type}")


# ── Custom Attack Execution ───────────────────────────────────────────────────

def run_custom_attack(request: CustomAttackRequest) -> AttackResult:
    """Run a user-written custom attack via the sandbox."""
    start_time = time.time()

    # Load model and sample
    classifier, model = load_model(request.model, request.dataset)
    image, true_label = get_sample(request.dataset, request.sample_index)
    x = image[np.newaxis, ...]

    # Original prediction
    orig_preds = classifier.predict(x)[0]
    orig_label = int(np.argmax(orig_preds))
    orig_conf = float(np.max(orig_preds))

    # Build context for user code
    context = {
        "classifier": classifier,
        "model": model,
        "image": image.copy(),
        "x": x.copy(),
        "true_label": true_label,
        "original_prediction": orig_preds.copy(),
        "params": request.params,
    }

    # Execute user code
    sandbox_result = execute_code(request.code, context=context)

    # Extract results
    frames = []
    for f in sandbox_result.get("frames", []):
        frames.append(AttackFrame(
            iteration=f.get("iteration", 0),
            image_base64=f.get("image_base64", ""),
            prediction=f.get("prediction", {}),
            loss=f.get("loss"),
            gradient_norm=f.get("gradient_norm"),
            metrics=f.get("metrics", {}),
        ))

    # Try to get the adversarial image from user code
    adv_result = sandbox_result.get("result")
    if adv_result is not None and isinstance(adv_result, np.ndarray):
        x_adv = adv_result if adv_result.ndim == 4 else adv_result[np.newaxis, ...]
    elif frames and frames[-1].image_base64:
        # Last frame has the adversarial image
        x_adv = x  # fallback
    else:
        x_adv = x.copy()

    # Get adversarial prediction
    adv_preds = classifier.predict(x_adv[:1])[0]
    adv_label = int(np.argmax(adv_preds))
    adv_conf = float(np.max(adv_preds))

    # Compute metrics
    metrics = compute_all_metrics(x[0], x_adv[0], orig_preds, adv_preds, true_label)
    noise = x_adv[0] - x[0]

    elapsed = time.time() - start_time

    stdout = sandbox_result.get("stdout", "")
    stderr = sandbox_result.get("stderr", "")
    if stderr:
        metrics["sandbox_error"] = 1.0

    return AttackResult(
        success=adv_label != true_label,
        original_label=orig_label,
        original_confidence=orig_conf,
        adversarial_label=adv_label,
        adversarial_confidence=adv_conf,
        original_image_base64=numpy_to_base64(x[0]),
        adversarial_image_base64=numpy_to_base64(x_adv[0]),
        noise_image_base64=numpy_to_base64(
            np.clip(noise * 10 + 0.5, 0, 1)
        ),
        frames=frames if frames else [
            AttackFrame(iteration=0, image_base64=numpy_to_base64(x[0]),
                        prediction={"label": orig_label, "confidence": orig_conf}),
            AttackFrame(iteration=1, image_base64=numpy_to_base64(x_adv[0]),
                        prediction={"label": adv_label, "confidence": adv_conf},
                        metrics=metrics),
        ],
        metrics=metrics,
        total_iterations=len(frames) if frames else 1,
        elapsed_seconds=round(elapsed, 3),
    )

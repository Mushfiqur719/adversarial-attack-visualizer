"""Metrics computation service — Lp norms, PSNR, SSIM."""

from __future__ import annotations

import numpy as np


def compute_l0(original: np.ndarray, adversarial: np.ndarray) -> float:
    """Number of pixels that changed."""
    diff = np.abs(original.flatten() - adversarial.flatten())
    return float(np.sum(diff > 1e-6))


def compute_l2(original: np.ndarray, adversarial: np.ndarray) -> float:
    """Euclidean distance between original and adversarial."""
    return float(np.linalg.norm(original.flatten() - adversarial.flatten()))


def compute_linf(original: np.ndarray, adversarial: np.ndarray) -> float:
    """Maximum absolute pixel change."""
    return float(np.max(np.abs(original.flatten() - adversarial.flatten())))


def compute_psnr(original: np.ndarray, adversarial: np.ndarray) -> float:
    """Peak Signal-to-Noise Ratio in dB."""
    mse = np.mean((original - adversarial) ** 2)
    if mse < 1e-10:
        return float("inf")
    max_val = 1.0 if original.max() <= 1.0 else 255.0
    return float(10.0 * np.log10(max_val ** 2 / mse))


def compute_ssim(original: np.ndarray, adversarial: np.ndarray) -> float:
    """Structural Similarity Index."""
    try:
        from skimage.metrics import structural_similarity as ssim

        # Handle (C, H, W) → (H, W, C)
        orig = original.copy()
        adv = adversarial.copy()

        if orig.ndim == 3 and orig.shape[0] in (1, 3):
            orig = np.transpose(orig, (1, 2, 0))
            adv = np.transpose(adv, (1, 2, 0))

        if orig.ndim == 3 and orig.shape[2] == 1:
            orig = orig.squeeze(2)
            adv = adv.squeeze(2)

        channel_axis = 2 if orig.ndim == 3 else None
        data_range = 1.0 if orig.max() <= 1.0 else 255.0
        return float(ssim(orig, adv, data_range=data_range,
                          channel_axis=channel_axis))
    except ImportError:
        # Fallback: simplified SSIM
        return _simple_ssim(original, adversarial)


def _simple_ssim(x: np.ndarray, y: np.ndarray) -> float:
    """Simplified SSIM approximation when skimage is not available."""
    c1 = (0.01 * 1.0) ** 2
    c2 = (0.03 * 1.0) ** 2
    mu_x = np.mean(x)
    mu_y = np.mean(y)
    sigma_x = np.var(x)
    sigma_y = np.var(y)
    sigma_xy = np.cov(x.flatten(), y.flatten())[0, 1]
    ssim_val = ((2 * mu_x * mu_y + c1) * (2 * sigma_xy + c2)) / \
               ((mu_x ** 2 + mu_y ** 2 + c1) * (sigma_x + sigma_y + c2))
    return float(ssim_val)


def compute_all_metrics(original: np.ndarray, adversarial: np.ndarray,
                        original_pred: np.ndarray, adversarial_pred: np.ndarray,
                        true_label: int) -> dict[str, float]:
    """Compute all metrics for an adversarial example."""
    orig_conf = float(original_pred[true_label]) if len(original_pred) > true_label else 0.0
    adv_label = int(np.argmax(adversarial_pred))
    adv_conf = float(np.max(adversarial_pred))
    success = adv_label != true_label

    return {
        "l0_norm": compute_l0(original, adversarial),
        "l2_norm": compute_l2(original, adversarial),
        "linf_norm": compute_linf(original, adversarial),
        "psnr": compute_psnr(original, adversarial),
        "ssim": compute_ssim(original, adversarial),
        "success": float(success),
        "original_confidence": orig_conf,
        "adversarial_confidence": adv_conf,
        "original_label": int(true_label),
        "adversarial_label": adv_label,
    }

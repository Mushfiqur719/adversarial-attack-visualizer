"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────────

class AttackType(str, Enum):
    FGSM = "fgsm"
    PGD = "pgd"
    CW = "cw"
    DEEPFOOL = "deepfool"
    SQUARE = "square"
    CUSTOM = "custom"


class DatasetName(str, Enum):
    MNIST = "mnist"
    FASHION_MNIST = "fashion_mnist"
    CIFAR10 = "cifar10"
    CIFAR100 = "cifar100"
    IMAGENET_SAMPLES = "imagenet_samples"
    CUSTOM = "custom"


class ModelName(str, Enum):
    SIMPLE_CNN_MNIST = "simple_cnn_mnist"
    RESNET18 = "resnet18"
    VGG16 = "vgg16"
    MOBILENET_V2 = "mobilenet_v2"


# ── Parameter Definitions ─────────────────────────────────────────────────────

class ParamDef(BaseModel):
    """A single user-definable parameter."""
    name: str
    label: str = ""
    type: str = "float"  # float, int, bool
    min: float | None = None
    max: float | None = None
    step: float | None = None
    default: float | int | bool = 0.0


# ── Attack Schemas ─────────────────────────────────────────────────────────────

class AttackConfig(BaseModel):
    """Configuration for launching an attack."""
    attack_type: AttackType
    dataset: DatasetName = DatasetName.MNIST
    model: ModelName = ModelName.SIMPLE_CNN_MNIST
    sample_index: int = 0
    params: dict[str, Any] = Field(default_factory=dict)
    targeted: bool = False
    target_label: int | None = None


class CustomAttackRequest(BaseModel):
    """Request to run user-written attack code."""
    code: str
    dataset: DatasetName = DatasetName.MNIST
    model: ModelName = ModelName.SIMPLE_CNN_MNIST
    sample_index: int = 0
    params: dict[str, Any] = Field(default_factory=dict)
    custom_params: list[ParamDef] = Field(default_factory=list)


class AttackFrame(BaseModel):
    """A single intermediate frame from an attack."""
    iteration: int
    image_base64: str
    noise_base64: str | None = None
    prediction: dict[str, Any] = Field(default_factory=dict)
    loss: float | None = None
    gradient_norm: float | None = None
    metrics: dict[str, float] = Field(default_factory=dict)


class AttackResult(BaseModel):
    """Final result of an attack run."""
    success: bool
    original_label: int
    original_confidence: float
    adversarial_label: int
    adversarial_confidence: float
    original_image_base64: str
    adversarial_image_base64: str
    noise_image_base64: str
    frames: list[AttackFrame] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
    total_iterations: int = 0
    elapsed_seconds: float = 0.0


# ── Dataset / Model Info ───────────────────────────────────────────────────────

class DatasetInfo(BaseModel):
    name: str
    display_name: str
    num_classes: int
    image_shape: list[int]
    num_samples: int
    sample_images: list[str] = Field(default_factory=list)  # base64


class ModelInfo(BaseModel):
    name: str
    display_name: str
    architecture: str
    compatible_datasets: list[str]
    num_parameters: int | None = None


# ── Metrics ────────────────────────────────────────────────────────────────────

class MetricsResult(BaseModel):
    l0_norm: float
    l2_norm: float
    linf_norm: float
    psnr: float
    ssim: float
    success_rate: float
    original_confidence: float
    adversarial_confidence: float


# ── Attack Registry ────────────────────────────────────────────────────────────

class AttackInfo(BaseModel):
    """Metadata about an available attack."""
    name: str
    display_name: str
    type: AttackType
    description: str
    params: list[ParamDef]
    is_iterative: bool = False


# ── Sandbox ────────────────────────────────────────────────────────────────────

class SandboxRequest(BaseModel):
    code: str
    timeout: int = 60


class SandboxResult(BaseModel):
    success: bool
    stdout: str = ""
    stderr: str = ""
    result: Any = None
    elapsed_seconds: float = 0.0

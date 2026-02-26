"""Model loading service — pretrained models wrapped in ART classifiers."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from app.config import get_device
from app.core.schemas import DatasetName, ModelInfo, ModelName

logger = logging.getLogger(__name__)

# ── Model cache ────────────────────────────────────────────────────────────────

_model_cache: dict[str, Any] = {}


# ── Simple CNN for MNIST ───────────────────────────────────────────────────────

class SimpleCNN_MNIST(nn.Module):
    """A small CNN for MNIST classification."""

    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def _create_mnist_model() -> nn.Module:
    """Create and initialize a simple MNIST CNN (untrained — for demo)."""
    model = SimpleCNN_MNIST()
    model.eval()
    return model


def _load_torchvision_model(name: str) -> nn.Module:
    """Load a pretrained model from torchvision."""
    import torchvision.models as models

    model_map = {
        "resnet18": lambda: models.resnet18(weights=models.ResNet18_Weights.DEFAULT),
        "vgg16": lambda: models.vgg16(weights=models.VGG16_Weights.DEFAULT),
        "mobilenet_v2": lambda: models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT),
    }
    if name not in model_map:
        raise ValueError(f"Unknown model: {name}")

    model = model_map[name]()
    model.eval()
    return model


def load_model(name: ModelName, dataset: DatasetName = DatasetName.MNIST):
    """
    Load a model and wrap it in an ART PyTorchClassifier.
    Returns (art_classifier, pytorch_model).
    """
    cache_key = f"{name.value}_{dataset.value}"
    if cache_key in _model_cache:
        return _model_cache[cache_key]

    from art.estimators.classification import PyTorchClassifier

    device = get_device()

    if name == ModelName.SIMPLE_CNN_MNIST:
        model = _create_mnist_model().to(device)
        input_shape = (1, 28, 28)
        nb_classes = 10
        clip_values = (0.0, 1.0)
    else:
        model = _load_torchvision_model(name.value).to(device)
        # ImageNet models always use (3, 224, 224) — the attack_service
        # handles adapting smaller inputs via _adapt_input()
        input_shape = (3, 224, 224)
        nb_classes = 1000
        clip_values = (0.0, 1.0)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    classifier = PyTorchClassifier(
        model=model,
        loss=loss_fn,
        optimizer=optimizer,
        input_shape=input_shape,
        nb_classes=nb_classes,
        clip_values=clip_values,
        device_type=device,
    )

    result = (classifier, model)
    _model_cache[cache_key] = result
    logger.info("Model loaded: %s for %s on %s", name.value, dataset.value, device)
    return result


def get_model_info(name: ModelName) -> ModelInfo:
    """Get metadata about a model."""
    info_map = {
        ModelName.SIMPLE_CNN_MNIST: ModelInfo(
            name="simple_cnn_mnist",
            display_name="Simple CNN (MNIST)",
            architecture="Conv2d(32) → Conv2d(64) → FC(128) → FC(10)",
            compatible_datasets=["mnist", "fashion_mnist"],
            num_parameters=206922,
        ),
        ModelName.RESNET18: ModelInfo(
            name="resnet18",
            display_name="ResNet-18 (ImageNet)",
            architecture="18-layer ResNet with skip connections",
            compatible_datasets=["mnist", "fashion_mnist", "cifar10", "cifar100", "imagenet_samples", "custom"],
            num_parameters=11689512,
        ),
        ModelName.VGG16: ModelInfo(
            name="vgg16",
            display_name="VGG-16 (ImageNet)",
            architecture="16-layer VGG with 3×3 convolutions",
            compatible_datasets=["mnist", "fashion_mnist", "cifar10", "cifar100", "imagenet_samples", "custom"],
            num_parameters=138357544,
        ),
        ModelName.MOBILENET_V2: ModelInfo(
            name="mobilenet_v2",
            display_name="MobileNet V2 (ImageNet)",
            architecture="Inverted residuals with linear bottleneck",
            compatible_datasets=["mnist", "fashion_mnist", "cifar10", "cifar100", "imagenet_samples", "custom"],
            num_parameters=3504872,
        ),
    }
    return info_map[name]


def list_models() -> list[ModelInfo]:
    """List all available models."""
    return [get_model_info(m) for m in ModelName]

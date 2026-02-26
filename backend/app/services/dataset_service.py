"""Dataset loading service — MNIST, Fashion-MNIST, CIFAR-10, CIFAR-100, ImageNet Samples."""

from __future__ import annotations

import base64
import io
import logging
import os
from typing import Any

import numpy as np
from PIL import Image

from app.config import get_settings
from app.core.schemas import DatasetInfo, DatasetName

logger = logging.getLogger(__name__)

# ── Dataset cache ──────────────────────────────────────────────────────────────

_dataset_cache: dict[str, dict[str, Any]] = {}


def _ensure_data_dir():
    os.makedirs(get_settings().DATA_DIR, exist_ok=True)


def _img_to_base64(img_array: np.ndarray) -> str:
    """Convert numpy image to base64 PNG."""
    img = img_array.copy()
    if img.ndim == 3 and img.shape[0] in (1, 3):
        img = np.transpose(img, (1, 2, 0))
    if img.ndim == 3 and img.shape[2] == 1:
        img = img.squeeze(2)
    if img.max() <= 1.0:
        img = (img * 255).astype(np.uint8)
    else:
        img = img.astype(np.uint8)
    pil_img = Image.fromarray(img)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def load_mnist() -> dict[str, Any]:
    """Load MNIST test set via torchvision."""
    if "mnist" in _dataset_cache:
        return _dataset_cache["mnist"]

    import torchvision.datasets as dsets
    import torchvision.transforms as T

    _ensure_data_dir()
    ds = dsets.MNIST(
        root=get_settings().DATA_DIR, train=False, download=True,
        transform=T.ToTensor(),
    )
    images = []
    labels = []
    for img_tensor, label in ds:
        images.append(img_tensor.numpy())
        labels.append(label)

    data = {
        "images": np.array(images, dtype=np.float32),
        "labels": np.array(labels, dtype=np.int64),
        "num_classes": 10,
        "image_shape": [1, 28, 28],
        "class_names": [str(i) for i in range(10)],
    }
    _dataset_cache["mnist"] = data
    logger.info("MNIST loaded: %d samples", len(labels))
    return data


def load_fashion_mnist() -> dict[str, Any]:
    """Load Fashion-MNIST test set via torchvision."""
    if "fashion_mnist" in _dataset_cache:
        return _dataset_cache["fashion_mnist"]

    import torchvision.datasets as dsets
    import torchvision.transforms as T

    _ensure_data_dir()
    ds = dsets.FashionMNIST(
        root=get_settings().DATA_DIR, train=False, download=True,
        transform=T.ToTensor(),
    )
    images = []
    labels = []
    for img_tensor, label in ds:
        images.append(img_tensor.numpy())
        labels.append(label)

    class_names = [
        "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
        "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot",
    ]
    data = {
        "images": np.array(images, dtype=np.float32),
        "labels": np.array(labels, dtype=np.int64),
        "num_classes": 10,
        "image_shape": [1, 28, 28],
        "class_names": class_names,
    }
    _dataset_cache["fashion_mnist"] = data
    logger.info("Fashion-MNIST loaded: %d samples", len(labels))
    return data


def load_cifar10() -> dict[str, Any]:
    """Load CIFAR-10 test set via torchvision."""
    if "cifar10" in _dataset_cache:
        return _dataset_cache["cifar10"]

    import torchvision.datasets as dsets
    import torchvision.transforms as T

    _ensure_data_dir()
    ds = dsets.CIFAR10(
        root=get_settings().DATA_DIR, train=False, download=True,
        transform=T.ToTensor(),
    )
    images = []
    labels = []
    for img_tensor, label in ds:
        images.append(img_tensor.numpy())
        labels.append(label)

    class_names = [
        "airplane", "automobile", "bird", "cat", "deer",
        "dog", "frog", "horse", "ship", "truck",
    ]
    data = {
        "images": np.array(images, dtype=np.float32),
        "labels": np.array(labels, dtype=np.int64),
        "num_classes": 10,
        "image_shape": [3, 32, 32],
        "class_names": class_names,
    }
    _dataset_cache["cifar10"] = data
    logger.info("CIFAR-10 loaded: %d samples", len(labels))
    return data


def load_cifar100() -> dict[str, Any]:
    """Load CIFAR-100 test set via torchvision."""
    if "cifar100" in _dataset_cache:
        return _dataset_cache["cifar100"]

    import torchvision.datasets as dsets
    import torchvision.transforms as T

    _ensure_data_dir()
    ds = dsets.CIFAR100(
        root=get_settings().DATA_DIR, train=False, download=True,
        transform=T.ToTensor(),
    )
    images = []
    labels = []
    for img_tensor, label in ds:
        images.append(img_tensor.numpy())
        labels.append(label)

    data = {
        "images": np.array(images, dtype=np.float32),
        "labels": np.array(labels, dtype=np.int64),
        "num_classes": 100,
        "image_shape": [3, 32, 32],
        "class_names": [str(i) for i in range(100)],
    }
    _dataset_cache["cifar100"] = data
    logger.info("CIFAR-100 loaded: %d samples", len(labels))
    return data


def load_imagenet_samples() -> dict[str, Any]:
    """
    Load ImageNet-compatible sample images.
    Uses CIFAR-10 images resized to 224×224 as ImageNet-scale RGB inputs.
    Maps CIFAR-10 classes to approximate ImageNet class IDs:
      airplane→404, automobile→436, bird→8, cat→281, deer→347,
      dog→207, frog→30, horse→340, ship→510, truck→555
    """
    if "imagenet_samples" in _dataset_cache:
        return _dataset_cache["imagenet_samples"]

    import torchvision.datasets as dsets
    import torchvision.transforms as T

    _ensure_data_dir()

    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
    ])

    ds = dsets.CIFAR10(
        root=get_settings().DATA_DIR, train=False, download=True,
        transform=transform,
    )

    # CIFAR-10 → approximate ImageNet class IDs
    cifar_to_imagenet = {
        0: 404,  # airplane → airliner
        1: 436,  # automobile → beach wagon
        2: 8,    # bird → hen
        3: 281,  # cat → tabby cat
        4: 347,  # deer → impala
        5: 207,  # dog → golden retriever
        6: 30,   # frog → bullfrog
        7: 340,  # horse → zebra
        8: 510,  # ship → container ship
        9: 555,  # truck → fire engine
    }
    imagenet_class_names = {
        404: "airliner", 436: "beach_wagon", 8: "hen", 281: "tabby_cat",
        347: "impala", 207: "golden_retriever", 30: "bullfrog", 340: "zebra",
        510: "container_ship", 555: "fire_engine",
    }

    # Take 50 samples per class (500 total) for manageable size
    per_class = 50
    class_counts = {i: 0 for i in range(10)}
    images = []
    labels = []
    for img_tensor, label in ds:
        if class_counts[label] < per_class:
            images.append(img_tensor.numpy())
            labels.append(cifar_to_imagenet[label])
            class_counts[label] += 1
        if all(c >= per_class for c in class_counts.values()):
            break

    data = {
        "images": np.array(images, dtype=np.float32),
        "labels": np.array(labels, dtype=np.int64),
        "num_classes": 1000,
        "image_shape": [3, 224, 224],
        "class_names": [imagenet_class_names.get(l, str(l)) for l in sorted(set(labels))],
    }
    _dataset_cache["imagenet_samples"] = data
    logger.info("ImageNet Samples loaded: %d images (from CIFAR-10 upscaled to 224×224)", len(labels))
    return data


def load_dataset(name: DatasetName) -> dict[str, Any]:
    """Load a dataset by name."""
    loaders = {
        DatasetName.MNIST: load_mnist,
        DatasetName.FASHION_MNIST: load_fashion_mnist,
        DatasetName.CIFAR10: load_cifar10,
        DatasetName.CIFAR100: load_cifar100,
        DatasetName.IMAGENET_SAMPLES: load_imagenet_samples,
    }
    if name not in loaders:
        raise ValueError(f"Unknown dataset: {name}")
    return loaders[name]()


# ── Dataset Metadata ───────────────────────────────────────────────────────────

DISPLAY_NAMES = {
    DatasetName.MNIST: "MNIST Handwritten Digits",
    DatasetName.FASHION_MNIST: "Fashion-MNIST",
    DatasetName.CIFAR10: "CIFAR-10 Objects",
    DatasetName.CIFAR100: "CIFAR-100 Fine-Grained",
    DatasetName.IMAGENET_SAMPLES: "ImageNet Samples (224×224)",
}

ALL_DATASETS = [
    DatasetName.MNIST,
    DatasetName.FASHION_MNIST,
    DatasetName.CIFAR10,
    DatasetName.CIFAR100,
    DatasetName.IMAGENET_SAMPLES,
]


def get_dataset_info(name: DatasetName) -> DatasetInfo:
    """Get metadata about a dataset (loads it if needed)."""
    data = load_dataset(name)
    sample_indices = list(range(min(8, len(data["images"]))))
    sample_images = [_img_to_base64(data["images"][i]) for i in sample_indices]

    return DatasetInfo(
        name=name.value,
        display_name=DISPLAY_NAMES.get(name, name.value),
        num_classes=data["num_classes"],
        image_shape=data["image_shape"],
        num_samples=len(data["images"]),
        sample_images=sample_images,
    )


def list_datasets() -> list[DatasetInfo]:
    """List all available datasets."""
    result = []
    for ds_name in ALL_DATASETS:
        try:
            info = get_dataset_info(ds_name)
            result.append(info)
        except Exception as e:
            logger.warning("Could not load %s: %s", ds_name, e)
            result.append(DatasetInfo(
                name=ds_name.value,
                display_name=DISPLAY_NAMES.get(ds_name, ds_name.value),
                num_classes=10,
                image_shape=[1, 28, 28],
                num_samples=0,
            ))
    return result


def get_sample(dataset: DatasetName, index: int) -> tuple[np.ndarray, int]:
    """Get a single sample image and label."""
    data = load_dataset(dataset)
    idx = index % len(data["images"])
    return data["images"][idx], int(data["labels"][idx])

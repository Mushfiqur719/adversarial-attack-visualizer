"""Application configuration using Pydantic Settings."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_TITLE: str = "Adversarial ML Visualization Platform"
    APP_VERSION: str = "1.0.0"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Device configuration
    DEVICE: str = "auto"  # "auto", "cuda", "cpu"

    # Upload directory for custom images
    UPLOAD_DIR: str = os.path.join(os.path.dirname(__file__), "..", "uploads")

    # Sandbox settings
    SANDBOX_TIMEOUT: int = 60  # seconds

    # Dataset cache directory
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "..", "data")

    class Config:
        env_prefix = "AML_"


def get_device() -> str:
    """Resolve the compute device (cuda/cpu)."""
    import torch

    settings = get_settings()
    if settings.DEVICE == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return settings.DEVICE


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

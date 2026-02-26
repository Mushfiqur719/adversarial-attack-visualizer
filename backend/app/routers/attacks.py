"""API routes for attack operations."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.schemas import AttackConfig, AttackResult, CustomAttackRequest
from app.services.attack_service import (
    get_attack_registry,
    run_builtin_attack,
    run_custom_attack,
)

router = APIRouter(prefix="/api/attacks", tags=["attacks"])


@router.get("/")
async def list_attacks():
    """List all available built-in attacks with their parameter definitions."""
    return get_attack_registry()


@router.post("/run", response_model=AttackResult)
async def run_attack(config: AttackConfig):
    """Run a built-in attack with the given parameters."""
    return run_builtin_attack(config)


@router.post("/run-custom", response_model=AttackResult)
async def run_custom(request: CustomAttackRequest):
    """Run user-written custom attack code."""
    return run_custom_attack(request)

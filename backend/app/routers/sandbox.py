"""API routes for sandbox code execution."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.schemas import SandboxRequest, SandboxResult
from app.services.sandbox_service import execute_code

router = APIRouter(prefix="/api/sandbox", tags=["sandbox"])


@router.post("/run", response_model=SandboxResult)
async def run_code(request: SandboxRequest):
    """Execute user-provided Python code in a sandboxed environment."""
    result = execute_code(request.code, timeout=request.timeout)
    return SandboxResult(
        success=result["success"],
        stdout=result["stdout"],
        stderr=result["stderr"],
        result=str(result.get("result", "")),
        elapsed_seconds=result["elapsed_seconds"],
    )

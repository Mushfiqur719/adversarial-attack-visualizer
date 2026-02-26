"""WebSocket handler for real-time attack streaming."""

from __future__ import annotations

import asyncio
import json
import logging
import traceback
from typing import Any

import numpy as np
from fastapi import WebSocket, WebSocketDisconnect

from app.core.schemas import AttackConfig, AttackType, CustomAttackRequest
from app.services.attack_service import run_builtin_attack, run_custom_attack

logger = logging.getLogger(__name__)


async def attack_websocket_handler(websocket: WebSocket):
    """
    WebSocket endpoint for real-time attack visualization.
    
    Protocol:
    1. Client connects and sends a JSON configuration message
    2. Server runs the attack and streams frames back
    3. Each frame is a JSON object with iteration data
    4. Final message has type="complete" with full results
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            # Wait for attack config from client
            raw = await websocket.receive_text()
            config_data = json.loads(raw)

            msg_type = config_data.get("type", "run")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if msg_type == "cancel":
                await websocket.send_json({"type": "cancelled"})
                continue

            # Send "started" acknowledgment
            await websocket.send_json({
                "type": "started",
                "attack_type": config_data.get("attack_type", "unknown"),
            })

            try:
                # Run attack in a thread pool to avoid blocking
                is_custom = config_data.get("attack_type") == "custom"

                if is_custom:
                    request = CustomAttackRequest(**config_data)
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, run_custom_attack, request
                    )
                else:
                    config = AttackConfig(**config_data)
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, run_builtin_attack, config
                    )

                # Stream frames one by one
                for i, frame in enumerate(result.frames):
                    await websocket.send_json({
                        "type": "frame",
                        "data": frame.model_dump(),
                    })
                    # Small delay to allow UI to render
                    await asyncio.sleep(0.05)

                # Send final result
                await websocket.send_json({
                    "type": "complete",
                    "data": result.model_dump(),
                })

            except Exception as e:
                logger.error("Attack execution error: %s", traceback.format_exc())
                await websocket.send_json({
                    "type": "error",
                    "message": str(e),
                    "traceback": traceback.format_exc(),
                })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error("WebSocket error: %s", e)

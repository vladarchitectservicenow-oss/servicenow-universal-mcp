# Copyright (c) 2026 Vlady
# SPDX-License-Identifier: AGPL-3.0-only

"""Structured logging — обёртка над стандартным logging с JSON-форматом.

Формат: {"timestamp": "2026-05-12T21:30:00Z", "level": "INFO", "module": "cli",
         "message": "...", "tool": "incident_create", "elapsed_ms": 45, ...}
"""

from __future__ import annotations

import json
import logging
import sys
import time
from contextvars import ContextVar
from typing import Any


# ── Context variables ─────────────────────────────────────────────────────

_tool_name: ContextVar[str] = ContextVar("tool_name", default="")
_request_id: ContextVar[str] = ContextVar("request_id", default="")


def set_tool(name: str) -> None:
    _tool_name.set(name)


def set_request(rid: str) -> None:
    _request_id.set(rid)


# ── JSON Formatter ─────────────────────────────────────────────────────────


class JSONFormatter(logging.Formatter):
    """Formats records as single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "module": record.name,
        }

        msg = record.getMessage()
        if isinstance(msg, dict):
            payload.update(msg)
        else:
            payload["message"] = msg

        if _tool_name.get():
            payload["tool"] = _tool_name.get()
        if _request_id.get():
            payload["request_id"] = _request_id.get()
        if record.exc_info and record.exc_info[1]:
            payload["exception"] = str(record.exc_info[1])

        return json.dumps(payload, ensure_ascii=False, default=str)


# ── Auto-config ────────────────────────────────────────────────────────────

_configured = False


def setup_logging(level: int = logging.INFO, json_output: bool = True):
    global _configured
    if _configured:
        return
    _configured = True

    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    if json_output:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s",
            )
        )

    root.handlers = [handler]

    # Silence noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("tenacity").setLevel(logging.WARNING)


# ── Timer context ──────────────────────────────────────────────────────────


class LogTimer:
    """Context manager that logs elapsed time."""

    def __init__(self, logger: logging.Logger, operation: str, **meta):
        self.logger = logger
        self.operation = operation
        self.meta = meta
        self.start: float = 0

    def __enter__(self):
        self.start = time.monotonic()
        return self

    def __exit__(self, *args):
        elapsed = (time.monotonic() - self.start) * 1000
        self.logger.info(
            {
                "operation": self.operation,
                "elapsed_ms": round(elapsed, 1),
                **self.meta,
            }
        )

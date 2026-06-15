from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

try:
    from langfuse import get_client, observe

    langfuse_client = get_client()
except Exception:  # pragma: no cover
    langfuse_client = None

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator


def tracing_enabled() -> bool:
    return bool(
        langfuse_client
        and os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
        and os.getenv("LANGFUSE_TRACING_ENABLED", "true").lower() != "false"
    )


def get_langfuse_client():
    return langfuse_client


def current_trace_id() -> str | None:
    if not langfuse_client:
        return None
    return langfuse_client.get_current_trace_id()


def flush_traces() -> None:
    if langfuse_client:
        langfuse_client.flush()

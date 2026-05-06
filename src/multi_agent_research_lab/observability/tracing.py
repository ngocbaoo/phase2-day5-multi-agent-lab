"""Tracing hooks."""

from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any
import logging

logger = logging.getLogger(__name__)

@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context used by the skeleton."""
    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    
    # E.g. integration with LangSmith could be added here
    # with langsmith.trace(name, "tool", metadata=attributes) as ls_trace:
    try:
        yield span
    finally:
        span["duration_seconds"] = perf_counter() - started
        logger.debug(f"Span {name} completed in {span['duration_seconds']:.2f}s")

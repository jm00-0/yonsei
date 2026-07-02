"""Three-line summary helpers with safe failure handling."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from typing import Any

logger = logging.getLogger(__name__)

COLLECTION_FAILED = "수집 실패"


def ensure_three_lines(lines: Iterable[str], fallback: str = COLLECTION_FAILED) -> list[str]:
    """Return exactly three non-empty lines."""

    cleaned = [line.strip() for line in lines if line and line.strip()]
    if not cleaned:
        cleaned = [fallback]

    while len(cleaned) < 3:
        cleaned.append(fallback)

    return cleaned[:3]


def item_to_text(item: Any) -> str:
    """Extract summary-like text from a dataclass or dictionary."""

    if isinstance(item, dict):
        for key in ("summary", "title", "text"):
            value = item.get(key)
            if value:
                return str(value)
        return ""

    for attr in ("summary", "title", "text"):
        value = getattr(item, attr, None)
        if value:
            return str(value)

    return str(item) if item else ""


def summarize_items(items: Iterable[Any]) -> list[str]:
    """Summarize items by taking the first three useful text snippets."""

    return ensure_three_lines(item_to_text(item) for item in items)


def collect_section(collector: Callable[[], Iterable[Any]]) -> list[str]:
    """Run a collector and convert failures into a visible section marker."""

    try:
        return summarize_items(collector())
    except Exception as exc:  # noqa: BLE001 - keep one failed section from stopping the run.
        logger.exception("Section collection failed: %s", exc)
        return ensure_three_lines([], fallback=COLLECTION_FAILED)

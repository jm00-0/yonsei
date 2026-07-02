"""KB Securities report source helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Iterable
from urllib.parse import urljoin

KB_SECURITIES_BASE_URL = "https://www.kbsec.com/"


@dataclass(frozen=True)
class Report:
    """Normalized securities report metadata."""

    stock_name: str
    title: str
    source: str
    url: str
    published_at: date | None = None


def normalize_report_items(
    items: Iterable[dict[str, Any]],
    base_url: str = KB_SECURITIES_BASE_URL,
) -> list[Report]:
    """Convert raw KB Securities-like report rows into Report objects."""

    reports: list[Report] = []

    for item in items:
        title = _first_text(item, "title", "report_title", "subject")
        url = _first_text(item, "url", "link", "href")
        stock_name = _first_text(item, "stock_name", "name", "company")

        if not title or not url:
            continue

        reports.append(
            Report(
                stock_name=stock_name or "unknown",
                title=title,
                source="KB Securities",
                url=urljoin(base_url, url),
                published_at=_parse_date(
                    _first_text(item, "published_at", "date", "created_at")
                ),
            )
        )

    return reports


def _first_text(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if value is None:
            continue

        text = str(value).strip()
        if text:
            return text

    return ""


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None

    for date_format in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value.strip(), date_format).date()
        except ValueError:
            continue

    return None

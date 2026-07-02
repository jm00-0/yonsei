"""News collection helpers for KOSPI newsletter generation."""

from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .market_data import StockMove

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NewsItem:
    """One news item connected to a stock."""

    symbol: str
    title: str
    url: str = ""
    summary: str = ""
    source: str = "news"


def load_news_items_from_csv(path: str | Path) -> list[NewsItem]:
    """Load prepared news rows from CSV.

    Expected columns: symbol,title,url,summary,source
    """

    items: list[NewsItem] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            symbol = (row.get("symbol") or "").strip()
            title = (row.get("title") or "").strip()
            if not symbol or not title:
                continue

            items.append(
                NewsItem(
                    symbol=symbol,
                    title=title,
                    url=(row.get("url") or "").strip(),
                    summary=(row.get("summary") or "").strip(),
                    source=(row.get("source") or "news").strip(),
                )
            )

    return items


def filter_news_for_stock(stock: StockMove, items: Iterable[NewsItem]) -> list[NewsItem]:
    """Return news items matching a stock symbol or name."""

    return [
        item
        for item in items
        if item.symbol == stock.symbol or stock.name in item.title
    ]


def fetch_news_for_stock(stock: StockMove) -> list[NewsItem]:
    """Fetch news for one stock from a prepared CSV source.

    Set NEWS_CSV to a licensed or allowed data file. This avoids relying on
    search-result scraping that may violate robots.txt or service terms.
    """

    csv_path = os.getenv("NEWS_CSV")
    if not csv_path:
        logger.warning("NEWS_CSV is not set. No news loaded for %s.", stock.symbol)
        return []

    try:
        return filter_news_for_stock(stock, load_news_items_from_csv(csv_path))
    except OSError as exc:
        logger.exception("Failed to load news CSV: %s", exc)
        raise

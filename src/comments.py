"""Investor comment collection helpers."""

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
class CommentItem:
    """One investor reaction or comment item."""

    symbol: str
    text: str
    source: str = "investor-comments"


def load_comment_items_from_csv(path: str | Path) -> list[CommentItem]:
    """Load prepared investor reaction rows from CSV.

    Expected columns: symbol,text,source
    """

    items: list[CommentItem] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            symbol = (row.get("symbol") or "").strip()
            text = (row.get("text") or row.get("comment") or "").strip()
            if not symbol or not text:
                continue

            items.append(
                CommentItem(
                    symbol=symbol,
                    text=text,
                    source=(row.get("source") or "investor-comments").strip(),
                )
            )

    return items


def filter_comments_for_stock(
    stock: StockMove,
    items: Iterable[CommentItem],
) -> list[CommentItem]:
    """Return comment items matching a stock symbol."""

    return [item for item in items if item.symbol == stock.symbol]


def fetch_comments_for_stock(stock: StockMove) -> list[CommentItem]:
    """Fetch investor comments from a prepared CSV source.

    Set COMMENTS_CSV to a file collected from sources that allow this use.
    """

    csv_path = os.getenv("COMMENTS_CSV")
    if not csv_path:
        logger.warning("COMMENTS_CSV is not set. No comments loaded for %s.", stock.symbol)
        return []

    try:
        return filter_comments_for_stock(stock, load_comment_items_from_csv(csv_path))
    except OSError as exc:
        logger.exception("Failed to load comments CSV: %s", exc)
        raise

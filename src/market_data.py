"""KOSPI market data loading and top mover selection."""

from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StockMove:
    """Daily stock movement used for newsletter targeting."""

    symbol: str
    name: str
    market: str
    change_rate: float


def parse_stock_move(row: dict[str, str]) -> StockMove:
    """Parse one CSV row into a StockMove."""

    return StockMove(
        symbol=(row.get("symbol") or row.get("code") or "").strip(),
        name=(row.get("name") or row.get("stock_name") or "").strip(),
        market=(row.get("market") or "").strip().upper(),
        change_rate=float((row.get("change_rate") or row.get("change_pct") or "0").strip()),
    )


def select_top_movers(
    moves: Iterable[StockMove],
    threshold: float = 5.0,
    limit: int = 10,
) -> list[StockMove]:
    """Select KOSPI stocks whose absolute change rate is at least threshold."""

    filtered = [
        move
        for move in moves
        if move.market == "KOSPI" and abs(move.change_rate) >= threshold
    ]
    return sorted(filtered, key=lambda move: abs(move.change_rate), reverse=True)[:limit]


def load_market_moves_from_csv(path: str | Path) -> list[StockMove]:
    """Load daily market moves from a UTF-8 CSV file."""

    moves: list[StockMove] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            try:
                move = parse_stock_move(row)
            except (TypeError, ValueError) as exc:
                logger.warning("Skipping invalid market row: %s", exc)
                continue

            if move.symbol and move.name:
                moves.append(move)

    return moves


def get_top_kospi_movers(
    csv_path: str | Path | None = None,
    threshold: float = 5.0,
    limit: int = 10,
) -> list[StockMove]:
    """Return top KOSPI movers from a configured CSV data source.

    Set KOSPI_MOVERS_CSV to a file with columns:
    symbol,name,market,change_rate
    """

    source_path = csv_path or os.getenv("KOSPI_MOVERS_CSV")
    if not source_path:
        logger.warning("KOSPI_MOVERS_CSV is not set. No market data loaded.")
        return []

    try:
        return select_top_movers(
            load_market_moves_from_csv(source_path),
            threshold=threshold,
            limit=limit,
        )
    except OSError as exc:
        logger.exception("Failed to load KOSPI market data: %s", exc)
        return []

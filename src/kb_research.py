"""KB Securities research collection helpers.

The module keeps crawling conservative. It checks robots.txt before fetching and
also supports a CSV input for repeatable tests and classroom runs.
"""

from __future__ import annotations

import csv
import logging
import os
import urllib.robotparser
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .market_data import StockMove

logger = logging.getLogger(__name__)

KB_SECURITIES_BASE_URL = "https://www.kbsec.com/"
USER_AGENT = "yonsei-stock-report-mailer/1.0"


@dataclass(frozen=True)
class ResearchItem:
    """One research item from KB Securities or a prepared CSV file."""

    symbol: str
    title: str
    url: str
    summary: str = ""
    source: str = "KB Securities"


def can_fetch(url: str, user_agent: str = USER_AGENT) -> bool:
    """Return whether robots.txt allows fetching the URL."""

    robots_url = urljoin(KB_SECURITIES_BASE_URL, "robots.txt")
    parser = urllib.robotparser.RobotFileParser(robots_url)

    try:
        parser.read()
    except OSError as exc:
        logger.warning("Could not read robots.txt: %s", exc)
        return False

    return parser.can_fetch(user_agent, url)


def load_research_items_from_csv(path: str | Path) -> list[ResearchItem]:
    """Load prepared research rows from CSV.

    Expected columns: symbol,title,url,summary
    """

    items: list[ResearchItem] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            symbol = (row.get("symbol") or "").strip()
            title = (row.get("title") or "").strip()
            url = (row.get("url") or "").strip()
            summary = (row.get("summary") or "").strip()
            if symbol and title:
                items.append(
                    ResearchItem(
                        symbol=symbol,
                        title=title,
                        url=urljoin(KB_SECURITIES_BASE_URL, url),
                        summary=summary,
                    )
                )

    return items


def filter_items_for_stock(
    stock: StockMove,
    items: Iterable[ResearchItem],
) -> list[ResearchItem]:
    """Return research items matching a stock symbol or name."""

    return [
        item
        for item in items
        if item.symbol == stock.symbol or stock.name in item.title
    ]


def fetch_kb_research_for_stock(stock: StockMove) -> list[ResearchItem]:
    """Fetch KB Securities research items for one stock.

    For stable classroom use, set KB_RESEARCH_CSV first. Live scraping is kept
    conservative because the exact official research endpoint may change.
    """

    csv_path = os.getenv("KB_RESEARCH_CSV")
    if csv_path:
        try:
            return filter_items_for_stock(stock, load_research_items_from_csv(csv_path))
        except OSError as exc:
            logger.exception("Failed to load KB research CSV: %s", exc)
            raise

    url = KB_SECURITIES_BASE_URL
    if not can_fetch(url):
        logger.warning("robots.txt does not allow fetching %s", url)
        return []

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.exception("Failed to fetch KB Securities page: %s", exc)
        raise

    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    if stock.name not in page_text and stock.symbol not in page_text:
        return []

    return [
        ResearchItem(
            symbol=stock.symbol,
            title=f"{stock.name} 관련 KB증권 페이지 확인",
            url=url,
            summary="KB증권 공식 사이트에서 종목명을 확인했습니다.",
        )
    ]

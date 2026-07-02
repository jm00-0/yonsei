import re
from html.parser import HTMLParser

from src.stock_scanner import select_top_kospi_movers


NAVER_MARKET_RISE_URL = "https://finance.naver.com/sise/sise_rise.naver?sosok=0"
NAVER_MARKET_FALL_URL = "https://finance.naver.com/sise/sise_fall.naver?sosok=0"
MARKET = "KOSPI"


def fetch_top_kospi_movers_from_naver(threshold=5.0, limit=10, html_fetcher=None):
    if html_fetcher is None:
        html_fetcher = _fetch_html

    stocks = [
        *parse_naver_mover_rows(html_fetcher(NAVER_MARKET_RISE_URL)),
        *parse_naver_mover_rows(html_fetcher(NAVER_MARKET_FALL_URL)),
    ]

    return select_top_kospi_movers(
        _dedupe_by_largest_move(stocks),
        threshold=threshold,
        limit=limit,
    )


def parse_naver_mover_rows(html):
    parser = _NaverMoverParser()
    parser.feed(html or "")
    return parser.stocks


def _dedupe_by_largest_move(stocks):
    by_code = {}
    for stock in stocks:
        existing = by_code.get(stock["code"])
        if existing is None or abs(stock["change_rate"]) > abs(existing["change_rate"]):
            by_code[stock["code"]] = stock
    return list(by_code.values())


def _fetch_html(url):
    import requests

    response = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    return response.text


def _clean_text(text):
    return " ".join(text.split())


def _parse_change_rate(text):
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text.replace(",", ""))
    if match is None:
        return None
    return float(match.group(0))


class _NaverMoverParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stocks = []
        self._current_row = None
        self._current_cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._current_row = {"cells": [], "code": None}
            return

        if self._current_row is None:
            return

        if tag == "td":
            self._current_cell = []
            return

        if tag == "a":
            href = dict(attrs).get("href", "")
            match = re.search(r"code=([0-9]{6})", href)
            if match:
                self._current_row["code"] = match.group(1)

    def handle_data(self, data):
        if self._current_cell is not None:
            self._current_cell.append(data)

    def handle_endtag(self, tag):
        if self._current_row is None:
            return

        if tag == "td" and self._current_cell is not None:
            self._current_row["cells"].append(_clean_text("".join(self._current_cell)))
            self._current_cell = None
            return

        if tag == "tr":
            self._finish_row()
            self._current_row = None
            self._current_cell = None

    def _finish_row(self):
        code = self._current_row.get("code")
        cells = self._current_row.get("cells", [])
        if not code or len(cells) < 2:
            return

        rate_text = next((cell for cell in cells if "%" in cell), "")
        change_rate = _parse_change_rate(rate_text)
        if change_rate is None:
            return

        self.stocks.append(
            {
                "code": code,
                "name": cells[1],
                "market": MARKET,
                "change_rate": change_rate,
            }
        )

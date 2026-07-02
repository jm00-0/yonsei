from src.data_sources.krx import fetch_kospi_stocks, fetch_top_kospi_movers


CHANGE_RATE_COLUMN = "\ub4f1\ub77d\ub960"


class FakePykrxFrame:
    def __init__(self, rows):
        self.rows = rows

    def iterrows(self):
        yield from self.rows


class FakePykrxStock:
    def __init__(self, rows, names):
        self.rows = rows
        self.names = names
        self.ohlcv_calls = []

    def get_market_ohlcv(self, date, market):
        self.ohlcv_calls.append((date, market))
        return FakePykrxFrame(self.rows)

    def get_market_ticker_name(self, ticker):
        return self.names[ticker]


def test_fetch_kospi_stocks_reads_pykrx_ohlcv_as_stock_dicts():
    stock_api = FakePykrxStock(
        rows=[
            ("005930", {CHANGE_RATE_COLUMN: 6.2}),
            ("000660", {CHANGE_RATE_COLUMN: -4.7}),
        ],
        names={
            "005930": "Samsung Electronics",
            "000660": "SK Hynix",
        },
    )

    result = fetch_kospi_stocks("2026-07-02", stock_api=stock_api)

    assert stock_api.ohlcv_calls == [("20260702", "KOSPI")]
    assert result == [
        {
            "code": "005930",
            "name": "Samsung Electronics",
            "market": "KOSPI",
            "change_rate": 6.2,
        },
        {
            "code": "000660",
            "name": "SK Hynix",
            "market": "KOSPI",
            "change_rate": -4.7,
        },
    ]


def test_fetch_top_kospi_movers_returns_top_10_from_pykrx_data():
    rows = [
        ("000001", {CHANGE_RATE_COLUMN: 4.99}),
        ("000002", {CHANGE_RATE_COLUMN: 5.0}),
        ("000003", {CHANGE_RATE_COLUMN: -8.1}),
        ("000004", {CHANGE_RATE_COLUMN: 12.0}),
        ("000005", {CHANGE_RATE_COLUMN: -11.0}),
        ("000006", {CHANGE_RATE_COLUMN: 10.0}),
        ("000007", {CHANGE_RATE_COLUMN: -9.0}),
        ("000008", {CHANGE_RATE_COLUMN: 8.0}),
        ("000009", {CHANGE_RATE_COLUMN: 7.0}),
        ("000010", {CHANGE_RATE_COLUMN: -6.0}),
        ("000011", {CHANGE_RATE_COLUMN: 5.5}),
        ("000012", {CHANGE_RATE_COLUMN: -5.2}),
    ]
    stock_api = FakePykrxStock(
        rows=rows,
        names={code: f"Stock {code}" for code, _ in rows},
    )

    result = fetch_top_kospi_movers("20260702", stock_api=stock_api)

    assert [stock["code"] for stock in result] == [
        "000004",
        "000005",
        "000006",
        "000007",
        "000003",
        "000008",
        "000009",
        "000010",
        "000011",
        "000012",
    ]


class FailingPykrxStock:
    def get_market_ohlcv(self, date, market):
        raise RuntimeError("KRX login failed")


def test_fetch_top_kospi_movers_falls_back_when_pykrx_fails():
    fallback_calls = []
    fallback_result = [
        {
            "code": "005930",
            "name": "Samsung Electronics",
            "market": "KOSPI",
            "change_rate": 7.4,
        }
    ]

    def fallback_fetcher(threshold, limit):
        fallback_calls.append((threshold, limit))
        return fallback_result

    result = fetch_top_kospi_movers(
        "2026-07-02",
        threshold=5.0,
        limit=10,
        stock_api=FailingPykrxStock(),
        fallback_fetcher=fallback_fetcher,
    )

    assert fallback_calls == [(5.0, 10)]
    assert result == fallback_result

from src.data_sources.krx import fetch_kospi_stocks, fetch_top_kospi_movers


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
            ("005930", {"등락률": 6.2}),
            ("000660", {"등락률": -4.7}),
        ],
        names={
            "005930": "삼성전자",
            "000660": "SK하이닉스",
        },
    )

    result = fetch_kospi_stocks("20260702", stock_api=stock_api)

    assert stock_api.ohlcv_calls == [("20260702", "KOSPI")]
    assert result == [
        {
            "code": "005930",
            "name": "삼성전자",
            "market": "KOSPI",
            "change_rate": 6.2,
        },
        {
            "code": "000660",
            "name": "SK하이닉스",
            "market": "KOSPI",
            "change_rate": -4.7,
        },
    ]


def test_fetch_top_kospi_movers_returns_top_10_from_pykrx_data():
    rows = [
        ("000001", {"등락률": 4.99}),
        ("000002", {"등락률": 5.0}),
        ("000003", {"등락률": -8.1}),
        ("000004", {"등락률": 12.0}),
        ("000005", {"등락률": -11.0}),
        ("000006", {"등락률": 10.0}),
        ("000007", {"등락률": -9.0}),
        ("000008", {"등락률": 8.0}),
        ("000009", {"등락률": 7.0}),
        ("000010", {"등락률": -6.0}),
        ("000011", {"등락률": 5.5}),
        ("000012", {"등락률": -5.2}),
    ]
    stock_api = FakePykrxStock(
        rows=rows,
        names={code: f"종목{code}" for code, _ in rows},
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

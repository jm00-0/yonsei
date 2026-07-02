from src.daily_source_collector import collect_daily_sources


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

    def get_market_ohlcv(self, date, market):
        return FakePykrxFrame(self.rows)

    def get_market_ticker_name(self, ticker):
        return self.names[ticker]


def test_collect_daily_sources_fetches_naver_candidates_for_top_kospi_movers():
    stock_api = FakePykrxStock(
        rows=[
            ("005930", {CHANGE_RATE_COLUMN: 8.2}),
            ("000660", {CHANGE_RATE_COLUMN: -6.1}),
            ("111111", {CHANGE_RATE_COLUMN: 3.0}),
        ],
        names={
            "005930": "Samsung Electronics",
            "000660": "SK Hynix",
            "111111": "Small Mover",
        },
    )

    fetched_urls = []

    def html_fetcher(url):
        fetched_urls.append(url)
        if "news.naver" in url:
            return '<a href="/item/news_read.naver?article_id=1&code=005930">News item</a>'
        if "board.naver" in url:
            return '<a href="/item/board_read.naver?code=005930&nid=10">Comment item</a>'
        if "company_list.naver" in url:
            return '<a href="/research/company_read.naver?nid=20">Research item</a>'
        return ""

    result = collect_daily_sources(
        "20260702",
        stock_api=stock_api,
        html_fetcher=html_fetcher,
    )

    assert [item["stock"]["code"] for item in result] == ["005930", "000660"]
    assert result[0]["stock"] == {
        "code": "005930",
        "name": "Samsung Electronics",
        "market": "KOSPI",
        "change_rate": 8.2,
    }
    assert result[0]["urls"] == {
        "main": "https://finance.naver.com/item/main.naver?code=005930",
        "news": "https://finance.naver.com/item/news_news.naver?code=005930&page=&clusterId=",
        "comment": "https://finance.naver.com/item/board.naver?code=005930",
        "research": "https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemCode=005930",
    }
    assert [source["source_type"] for source in result[0]["sources"]] == [
        "news",
        "comment",
        "research",
    ]
    assert fetched_urls == [
        "https://finance.naver.com/item/news_news.naver?code=005930&page=&clusterId=",
        "https://finance.naver.com/item/board.naver?code=005930",
        "https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemCode=005930",
        "https://finance.naver.com/item/news_news.naver?code=000660&page=&clusterId=",
        "https://finance.naver.com/item/board.naver?code=000660",
        "https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemCode=000660",
    ]

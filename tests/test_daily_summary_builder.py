from src.daily_summary_builder import (
    extract_text_from_html,
    summarize_daily_sources,
    summarize_relevant_text,
)


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


def test_extract_text_from_html_removes_markup_and_scripts():
    html = """
    <html>
      <head><style>.hidden { display: none; }</style></head>
      <body>
        <h1>Headline</h1>
        <script>alert("skip");</script>
        <p>First reason sentence.</p>
        <p>Second reason sentence.</p>
      </body>
    </html>
    """

    result = extract_text_from_html(html)

    assert result == "Headline First reason sentence. Second reason sentence."


def test_summarize_relevant_text_returns_three_reason_focused_lines():
    stock = {
        "code": "005930",
        "name": "Samsung Electronics",
        "market": "KOSPI",
        "change_rate": -8.2,
    }
    documents = [
        {
            "title": "Samsung Electronics falls sharply",
            "url": "https://finance.naver.com/item/news_read.naver?article_id=1",
            "source_type": "news",
            "text": (
                "Market chatter was noisy. "
                "Samsung Electronics fell after weaker earnings guidance. "
                "Foreign selling pressured semiconductor shares. "
                "Memory demand concerns added to the decline."
            ),
        }
    ]

    result = summarize_relevant_text(stock, "news", documents)

    assert result == [
        "Samsung Electronics fell after weaker earnings guidance.",
        "Foreign selling pressured semiconductor shares.",
        "Memory demand concerns added to the decline.",
    ]


def test_summarize_relevant_text_falls_back_to_candidate_titles():
    stock = {
        "code": "002780",
        "name": "Jinheung Enterprise",
        "market": "KOSPI",
        "change_rate": 29.92,
    }
    documents = [
        {
            "title": "Shareholders ask what happens next",
            "url": "https://finance.naver.com/item/board_read.naver?code=002780&nid=1",
            "source_type": "comment",
            "text": "",
        },
        {
            "title": "Board users compare short-term views",
            "url": "https://finance.naver.com/item/board_read.naver?code=002780&nid=2",
            "source_type": "comment",
            "text": "",
        },
    ]

    result = summarize_relevant_text(stock, "comment", documents)

    assert result == [
        "Candidate comment: Shareholders ask what happens next",
        "Candidate comment: Board users compare short-term views",
        "No additional comment source was collected.",
    ]


def test_summarize_relevant_text_ignores_unreadably_long_page_text():
    stock = {
        "code": "002780",
        "name": "Jinheung Enterprise",
        "market": "KOSPI",
        "change_rate": 29.92,
    }
    documents = [
        {
            "title": "Limit-up move draws investor attention",
            "url": "https://finance.naver.com/item/board_read.naver?code=002780&nid=1",
            "source_type": "comment",
            "text": "Jinheung Enterprise " + ("navigation menu market data " * 40),
        }
    ]

    result = summarize_relevant_text(stock, "comment", documents)

    assert result == [
        "Candidate comment: Limit-up move draws investor attention",
        "No additional comment source was collected.",
        "No additional comment source was collected.",
    ]


def test_summarize_daily_sources_fetches_bodies_and_groups_three_line_summaries():
    stock_api = FakePykrxStock(
        rows=[
            ("005930", {CHANGE_RATE_COLUMN: -8.2}),
            ("111111", {CHANGE_RATE_COLUMN: 3.0}),
        ],
        names={
            "005930": "Samsung Electronics",
            "111111": "Small Mover",
        },
    )
    fetched_detail_urls = []

    def list_html_fetcher(url):
        if "news.naver" in url:
            return '<a href="/item/news_read.naver?article_id=1&code=005930">News title</a>'
        if "board.naver" in url:
            return '<a href="/item/board_read.naver?code=005930&nid=10">Comment title</a>'
        if "company_list.naver" in url:
            return '<a href="/research/company_read.naver?nid=20">Research title</a>'
        return ""

    def detail_html_fetcher(url):
        fetched_detail_urls.append(url)
        return f"<html><body><h1>{url}</h1><p>Body text about today's move.</p></body></html>"

    def summarizer(stock, source_type, documents, lines_per_type):
        assert stock["code"] == "005930"
        assert lines_per_type == 3
        assert len(documents) == 1
        assert "Body text about today's move." in documents[0]["text"]
        return [
            f"{source_type} summary 1",
            f"{source_type} summary 2",
            f"{source_type} summary 3",
        ]

    result = summarize_daily_sources(
        "20260702",
        stock_api=stock_api,
        list_html_fetcher=list_html_fetcher,
        detail_html_fetcher=detail_html_fetcher,
        summarizer=summarizer,
    )

    assert len(result) == 1
    assert result[0]["stock"]["code"] == "005930"
    assert result[0]["summaries"] == {
        "news": ["news summary 1", "news summary 2", "news summary 3"],
        "comment": ["comment summary 1", "comment summary 2", "comment summary 3"],
        "research": ["research summary 1", "research summary 2", "research summary 3"],
    }
    assert [doc["source_type"] for doc in result[0]["source_documents"]] == [
        "news",
        "comment",
        "research",
    ]
    assert fetched_detail_urls == [
        "https://finance.naver.com/item/news_read.naver?article_id=1&code=005930",
        "https://finance.naver.com/item/board_read.naver?code=005930&nid=10",
        "https://finance.naver.com/research/company_read.naver?nid=20",
    ]

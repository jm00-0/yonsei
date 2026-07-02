from src.data_sources.naver_finance import (
    build_naver_finance_urls,
    collect_source_links_from_html,
    parse_comment_links,
    parse_news_links,
    parse_research_links,
)


def test_builds_naver_finance_urls_for_stock_code():
    urls = build_naver_finance_urls("5930")

    assert urls == {
        "main": "https://finance.naver.com/item/main.naver?code=005930",
        "news": "https://finance.naver.com/item/news_news.naver?code=005930&page=&clusterId=",
        "comment": "https://finance.naver.com/item/board.naver?code=005930",
        "research": "https://finance.naver.com/research/company_list.naver?searchType=itemCode&itemCode=005930",
    }


def test_parse_news_links_returns_normalized_candidate_links():
    html = """
    <html>
      <body>
        <a href="/item/news_read.naver?article_id=1&office_id=001&code=005930">
          Samsung Electronics jumps on earnings news
        </a>
        <a href="/item/news_news.naver?code=005930&page=2">Next</a>
        <a href="#none">Ignored link</a>
        <a href="/item/news_read.naver?article_id=1&office_id=001&code=005930">
          Duplicate news
        </a>
      </body>
    </html>
    """

    result = parse_news_links(html)

    assert result == [
        {
            "title": "Samsung Electronics jumps on earnings news",
            "url": "https://finance.naver.com/item/news_read.naver?article_id=1&office_id=001&code=005930",
            "source_type": "news",
        }
    ]


def test_parse_comment_links_returns_board_candidates():
    html = """
    <table>
      <tr>
        <td>
          <a href="/item/board_read.naver?code=005930&nid=123&page=1">
            Investors discuss the sharp move
          </a>
        </td>
      </tr>
      <tr>
        <td><a href="/item/board.naver?code=005930&page=2">2</a></td>
      </tr>
    </table>
    """

    result = parse_comment_links(html)

    assert result == [
        {
            "title": "Investors discuss the sharp move",
            "url": "https://finance.naver.com/item/board_read.naver?code=005930&nid=123&page=1",
            "source_type": "comment",
        }
    ]


def test_parse_research_links_returns_company_report_candidates():
    html = """
    <div>
      <a href="company_read.naver?nid=999&page=1&searchType=itemCode&itemCode=005930">
        Samsung Electronics target price raised
      </a>
      <a href="/research/company_list.naver?page=2">Next</a>
    </div>
    """

    result = parse_research_links(html)

    assert result == [
        {
            "title": "Samsung Electronics target price raised",
            "url": "https://finance.naver.com/research/company_read.naver?nid=999&page=1&searchType=itemCode&itemCode=005930",
            "source_type": "research",
        }
    ]


def test_collect_source_links_from_html_combines_news_comments_and_research():
    result = collect_source_links_from_html(
        news_html='<a href="/item/news_read.naver?article_id=1&code=005930">News</a>',
        comment_html='<a href="/item/board_read.naver?code=005930&nid=10">Comment</a>',
        research_html='<a href="company_read.naver?nid=20">Research</a>',
    )

    assert [item["source_type"] for item in result] == [
        "news",
        "comment",
        "research",
    ]

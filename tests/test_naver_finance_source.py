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
        "news": "https://finance.naver.com/item/news.naver?code=005930",
        "comment": "https://finance.naver.com/item/board.naver?code=005930",
        "research": "https://finance.naver.com/item/coinfo.naver?code=005930",
    }


def test_parse_news_links_returns_normalized_candidate_links():
    html = """
    <html>
      <body>
        <a href="/item/news_read.naver?article_id=1&office_id=001&code=005930">
          삼성전자 급락 관련 뉴스
        </a>
        <a href="/item/news.naver?code=005930&page=2">다음</a>
        <a href="#none">무시할 링크</a>
        <a href="/item/news_read.naver?article_id=1&office_id=001&code=005930">
          중복 뉴스
        </a>
      </body>
    </html>
    """

    result = parse_news_links(html)

    assert result == [
        {
            "title": "삼성전자 급락 관련 뉴스",
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
            실적이 걱정됩니다
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
            "title": "실적이 걱정됩니다",
            "url": "https://finance.naver.com/item/board_read.naver?code=005930&nid=123&page=1",
            "source_type": "comment",
        }
    ]


def test_parse_research_links_returns_company_report_candidates():
    html = """
    <div>
      <a href="/research/company_read.naver?nid=999&page=1">
        삼성전자 목표가 상향
      </a>
      <a href="/research/company_list.naver?page=2">다음</a>
    </div>
    """

    result = parse_research_links(html)

    assert result == [
        {
            "title": "삼성전자 목표가 상향",
            "url": "https://finance.naver.com/research/company_read.naver?nid=999&page=1",
            "source_type": "research",
        }
    ]


def test_collect_source_links_from_html_combines_news_comments_and_research():
    result = collect_source_links_from_html(
        news_html='<a href="/item/news_read.naver?article_id=1&code=005930">뉴스</a>',
        comment_html='<a href="/item/board_read.naver?code=005930&nid=10">댓글</a>',
        research_html='<a href="/research/company_read.naver?nid=20">리서치</a>',
    )

    assert [item["source_type"] for item in result] == [
        "news",
        "comment",
        "research",
    ]

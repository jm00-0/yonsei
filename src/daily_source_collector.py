from src.data_sources.krx import fetch_top_kospi_movers
from src.data_sources.naver_finance import (
    build_naver_finance_urls,
    parse_comment_links,
    parse_news_links,
    parse_research_links,
)


def collect_daily_sources(
    date,
    stock_api=None,
    html_fetcher=None,
    threshold=5.0,
    limit=10,
    per_source_limit=None,
):
    if html_fetcher is None:
        html_fetcher = _fetch_html

    stocks = fetch_top_kospi_movers(
        date,
        threshold=threshold,
        limit=limit,
        stock_api=stock_api,
    )

    return [
        _collect_stock_sources(stock, html_fetcher, per_source_limit)
        for stock in stocks
    ]


def _collect_stock_sources(stock, html_fetcher, per_source_limit):
    urls = build_naver_finance_urls(stock["code"])
    news_html = html_fetcher(urls["news"])
    comment_html = html_fetcher(urls["comment"])
    research_html = html_fetcher(urls["research"])

    sources = [
        *parse_news_links(news_html, limit=per_source_limit),
        *parse_comment_links(comment_html, limit=per_source_limit),
        *parse_research_links(research_html, limit=per_source_limit),
    ]

    return {
        "stock": stock,
        "urls": urls,
        "sources": sources,
    }


def _fetch_html(url):
    import requests

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text

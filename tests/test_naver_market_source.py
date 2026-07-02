from src.data_sources.naver_market import (
    NAVER_MARKET_FALL_URL,
    NAVER_MARKET_RISE_URL,
    fetch_top_kospi_movers_from_naver,
    parse_naver_mover_rows,
)


RISE_HTML = """
<table class="type_2">
  <tr>
    <td class="no">1</td>
    <td><a href="/item/main.naver?code=005930" class="tltle">Samsung Electronics</a></td>
    <td class="number">80,000</td>
    <td class="number">4,800</td>
    <td class="number"><span class="tah p11 red01">+6.25%</span></td>
  </tr>
  <tr>
    <td class="no">2</td>
    <td><a href="/item/main.naver?code=000660" class="tltle">SK Hynix</a></td>
    <td class="number">200,000</td>
    <td class="number">9,000</td>
    <td class="number"><span class="tah p11 red01">+4.71%</span></td>
  </tr>
</table>
"""


FALL_HTML = """
<table class="type_2">
  <tr>
    <td class="no">1</td>
    <td><a href="/item/main.naver?code=051910" class="tltle">LG Chem</a></td>
    <td class="number">300,000</td>
    <td class="number">27,000</td>
    <td class="number"><span class="tah p11 nv01">-8.26%</span></td>
  </tr>
</table>
"""


def test_parse_naver_mover_rows_extracts_stock_code_name_and_change_rate():
    result = parse_naver_mover_rows(RISE_HTML)

    assert result == [
        {
            "code": "005930",
            "name": "Samsung Electronics",
            "market": "KOSPI",
            "change_rate": 6.25,
        },
        {
            "code": "000660",
            "name": "SK Hynix",
            "market": "KOSPI",
            "change_rate": 4.71,
        },
    ]


def test_fetch_top_kospi_movers_from_naver_combines_rise_and_fall_pages():
    fetched_urls = []

    def html_fetcher(url):
        fetched_urls.append(url)
        if url == NAVER_MARKET_RISE_URL:
            return RISE_HTML
        if url == NAVER_MARKET_FALL_URL:
            return FALL_HTML
        raise AssertionError(f"Unexpected URL: {url}")

    result = fetch_top_kospi_movers_from_naver(
        threshold=5.0,
        limit=10,
        html_fetcher=html_fetcher,
    )

    assert fetched_urls == [NAVER_MARKET_RISE_URL, NAVER_MARKET_FALL_URL]
    assert [stock["code"] for stock in result] == ["051910", "005930"]

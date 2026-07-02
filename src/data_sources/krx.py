from src.data_sources.naver_market import fetch_top_kospi_movers_from_naver
from src.stock_scanner import select_top_kospi_movers


CHANGE_RATE_COLUMN = "\ub4f1\ub77d\ub960"


def fetch_kospi_stocks(date, stock_api=None):
    if stock_api is None:
        stock_api = _load_pykrx_stock_api()

    ohlcv = stock_api.get_market_ohlcv(_format_pykrx_date(date), market="KOSPI")
    stocks = []

    for ticker, row in ohlcv.iterrows():
        code = str(ticker).zfill(6)
        stocks.append(
            {
                "code": code,
                "name": stock_api.get_market_ticker_name(code),
                "market": "KOSPI",
                "change_rate": float(row[CHANGE_RATE_COLUMN]),
            }
        )

    return stocks


def fetch_top_kospi_movers(
    date,
    threshold=5.0,
    limit=10,
    stock_api=None,
    fallback_fetcher=fetch_top_kospi_movers_from_naver,
):
    try:
        stocks = fetch_kospi_stocks(date, stock_api=stock_api)
    except Exception as exc:
        print(
            "pykrx KOSPI fetch failed; "
            f"falling back to Naver Finance movers: {exc}"
        )
        return fallback_fetcher(threshold=threshold, limit=limit)

    return select_top_kospi_movers(stocks, threshold=threshold, limit=limit)


def _format_pykrx_date(date):
    return str(date).replace("-", "")


def _load_pykrx_stock_api():
    try:
        from pykrx import stock
    except ImportError as exc:
        raise RuntimeError(
            "pykrx is required to fetch KRX market data. "
            "Install dependencies with `pip install -r requirements.txt`."
        ) from exc

    return stock

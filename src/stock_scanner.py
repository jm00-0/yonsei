def select_top_kospi_movers(stocks, threshold=5.0, limit=10):
    kospi_movers = [
        stock
        for stock in stocks
        if stock.get("market") == "KOSPI"
        and abs(stock.get("change_rate", 0)) >= threshold
    ]

    return sorted(
        kospi_movers,
        key=lambda stock: abs(stock["change_rate"]),
        reverse=True,
    )[:limit]

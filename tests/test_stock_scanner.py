from src.stock_scanner import select_top_kospi_movers


def test_selects_top_10_kospi_movers_by_absolute_change_rate():
    stocks = [
        {"code": "000001", "name": "One", "market": "KOSPI", "change_rate": 4.99},
        {"code": "000002", "name": "Two", "market": "KOSPI", "change_rate": 5.0},
        {"code": "000003", "name": "Three", "market": "KOSPI", "change_rate": -8.1},
        {"code": "000004", "name": "Four", "market": "KOSDAQ", "change_rate": 20.0},
        {"code": "000005", "name": "Five", "market": "KOSPI", "change_rate": -5.0},
        {"code": "000006", "name": "Six", "market": "KOSPI", "change_rate": 12.0},
        {"code": "000007", "name": "Seven", "market": "KOSPI", "change_rate": -11.0},
        {"code": "000008", "name": "Eight", "market": "KOSPI", "change_rate": 10.0},
        {"code": "000009", "name": "Nine", "market": "KOSPI", "change_rate": -9.0},
        {"code": "000010", "name": "Ten", "market": "KOSPI", "change_rate": 8.0},
        {"code": "000011", "name": "Eleven", "market": "KOSPI", "change_rate": 7.0},
        {"code": "000012", "name": "Twelve", "market": "KOSPI", "change_rate": -6.0},
        {"code": "000013", "name": "Thirteen", "market": "KOSPI", "change_rate": 5.5},
        {"code": "000014", "name": "Fourteen", "market": "KOSPI", "change_rate": -5.2},
    ]

    result = select_top_kospi_movers(stocks)

    assert [stock["code"] for stock in result] == [
        "000006",
        "000007",
        "000008",
        "000009",
        "000003",
        "000010",
        "000011",
        "000012",
        "000013",
        "000014",
    ]


def test_returns_empty_list_when_no_kospi_stock_moves_at_least_5_percent():
    stocks = [
        {"code": "100001", "name": "Small Move", "market": "KOSPI", "change_rate": 4.9},
        {"code": "100002", "name": "Other Market", "market": "KOSDAQ", "change_rate": -7.3},
    ]

    result = select_top_kospi_movers(stocks)

    assert result == []

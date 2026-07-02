from src.report_writer import build_report_filename, write_markdown_reports


def test_build_report_filename_uses_code_and_safe_stock_name():
    assert build_report_filename("005930", "Samsung Electronics") == "005930-samsung-electronics.md"
    assert build_report_filename("000660", "SK/Hynix: Inc.") == "000660-sk-hynix-inc.md"
    assert build_report_filename("123", "  Weird  Name  ") == "000123-weird-name.md"


def test_write_markdown_reports_creates_index_and_stock_detail_files(tmp_path):
    summaries = [
        {
            "stock": {
                "code": "005930",
                "name": "Samsung Electronics",
                "market": "KOSPI",
                "change_rate": -8.2,
            },
            "summaries": {
                "news": [
                    "News reason 1.",
                    "News reason 2.",
                    "News reason 3.",
                ],
                "comment": [
                    "Comment reason 1.",
                    "Comment reason 2.",
                    "Comment reason 3.",
                ],
                "research": [
                    "Research reason 1.",
                    "Research reason 2.",
                    "Research reason 3.",
                ],
            },
            "source_documents": [
                {
                    "title": "News title",
                    "url": "https://finance.naver.com/item/news_read.naver?article_id=1",
                    "source_type": "news",
                    "text": "News body",
                },
                {
                    "title": "Comment title",
                    "url": "https://finance.naver.com/item/board_read.naver?nid=10",
                    "source_type": "comment",
                    "text": "Comment body",
                },
                {
                    "title": "Research title",
                    "url": "https://finance.naver.com/research/company_read.naver?nid=20",
                    "source_type": "research",
                    "text": "Research body",
                },
            ],
        },
        {
            "stock": {
                "code": "000660",
                "name": "SK/Hynix: Inc.",
                "market": "KOSPI",
                "change_rate": 6.1,
            },
            "summaries": {
                "news": ["Another news 1.", "Another news 2.", "Another news 3."],
                "comment": ["Another comment 1.", "Another comment 2.", "Another comment 3."],
                "research": ["Another research 1.", "Another research 2.", "Another research 3."],
            },
            "source_documents": [],
        },
    ]

    result = write_markdown_reports(summaries, "2026-07-02", output_root=tmp_path)

    report_dir = tmp_path / "2026-07-02"
    index_path = report_dir / "index.md"
    samsung_path = report_dir / "005930-samsung-electronics.md"
    hynix_path = report_dir / "000660-sk-hynix-inc.md"

    assert result == {
        "report_dir": report_dir,
        "index": index_path,
        "details": [samsung_path, hynix_path],
    }
    assert index_path.exists()
    assert samsung_path.exists()
    assert hynix_path.exists()

    index_text = index_path.read_text(encoding="utf-8")
    assert "# 2026-07-02 KOSPI Daily Report" in index_text
    assert "| Samsung Electronics | 005930 | -8.20% | [details](005930-samsung-electronics.md) |" in index_text
    assert "| SK/Hynix: Inc. | 000660 | +6.10% | [details](000660-sk-hynix-inc.md) |" in index_text

    samsung_text = samsung_path.read_text(encoding="utf-8")
    assert "# Samsung Electronics (005930)" in samsung_text
    assert "- Date: 2026-07-02" in samsung_text
    assert "- Change rate: -8.20%" in samsung_text
    assert "## News Summary" in samsung_text
    assert "1. News reason 1." in samsung_text
    assert "## Comment Summary" in samsung_text
    assert "2. Comment reason 2." in samsung_text
    assert "## Research Summary" in samsung_text
    assert "3. Research reason 3." in samsung_text
    assert "- [News title](https://finance.naver.com/item/news_read.naver?article_id=1) - news" in samsung_text
    assert "- [Comment title](https://finance.naver.com/item/board_read.naver?nid=10) - comment" in samsung_text
    assert "- [Research title](https://finance.naver.com/research/company_read.naver?nid=20) - research" in samsung_text

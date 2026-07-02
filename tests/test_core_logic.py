from datetime import date, datetime, timedelta
from pathlib import Path

from src.gmail_sender import GmailSettings, build_email_draft, to_email_message
from src.market_data import StockMove, select_top_movers
from src.markdown_writer import Newsletter, NewsletterEntry, render_newsletter, write_newsletter
from src.scheduler import seconds_until_next_run
from src.summarizer import COLLECTION_FAILED, collect_section, ensure_three_lines


def test_select_top_kospi_movers_uses_absolute_change_rate_and_limit():
    moves = [
        StockMove("000001", "A", "KOSPI", 4.9),
        StockMove("000002", "B", "KOSPI", -7.0),
        StockMove("000003", "C", "KOSDAQ", 9.0),
        StockMove("000004", "D", "KOSPI", 6.0),
        StockMove("000005", "E", "KOSPI", -5.5),
    ]

    result = select_top_movers(moves, threshold=5.0, limit=2)

    assert [move.symbol for move in result] == ["000002", "000004"]


def test_ensure_three_lines_fills_missing_lines():
    result = ensure_three_lines(["첫 줄"])

    assert result == ["첫 줄", COLLECTION_FAILED, COLLECTION_FAILED]


def test_collect_section_returns_failure_lines_when_collector_raises():
    def broken_collector():
        raise RuntimeError("boom")

    result = collect_section(broken_collector)

    assert result == [COLLECTION_FAILED, COLLECTION_FAILED, COLLECTION_FAILED]


def test_render_newsletter_contains_three_sections():
    stock = StockMove("005930", "삼성전자", "KOSPI", 5.25)
    newsletter = Newsletter(
        as_of=date(2026, 7, 2),
        entries=[
            NewsletterEntry(
                stock=stock,
                research_summary=["리서치1", "리서치2", "리서치3"],
                comment_summary=["댓글1", "댓글2", "댓글3"],
                news_summary=["뉴스1", "뉴스2", "뉴스3"],
            )
        ],
    )

    markdown = render_newsletter(newsletter)

    assert "# 2026-07-02 KOSPI 일일 리서치/뉴스레터" in markdown
    assert "### 리서치 요약" in markdown
    assert "### 댓글/투자자 반응 요약" in markdown
    assert "### 뉴스 요약" in markdown


def test_write_newsletter_uses_dated_output_folder(tmp_path: Path):
    newsletter = Newsletter(as_of=date(2026, 7, 2), entries=[])

    output_path = write_newsletter(newsletter, output_root=tmp_path)

    assert output_path == tmp_path / "2026-07-02" / "newsletter.md"
    assert output_path.exists()


def test_email_draft_uses_environment_values_without_sending(tmp_path: Path):
    newsletter_path = tmp_path / "newsletter.md"
    newsletter_path.write_text("# 제목\n\n## 종목\n\n### 뉴스 요약\n- 본문", encoding="utf-8")
    settings = GmailSettings(
        sender="ssou56@gmail.com",
        recipient="recipient@example.com",
        credentials_path="credentials.json",
        timezone="Asia/Seoul",
    )

    draft = build_email_draft(newsletter_path, date(2026, 7, 2), settings)
    message = to_email_message(draft)

    assert draft.subject == "[2026-07-02] KOSPI 일일 리서치/뉴스레터"
    assert message["From"] == "ssou56@gmail.com"
    assert message["To"] == "recipient@example.com"
    assert "본문" in message.get_body(("plain",)).get_content()


def test_email_draft_contains_html_newsletter_body(tmp_path: Path):
    newsletter_path = tmp_path / "newsletter.md"
    newsletter_path.write_text(
        "# 2026-07-02 KOSPI 일일 리서치/뉴스레터\n\n"
        "## 1. 삼성전자 (005930) +5.25%\n\n"
        "### 뉴스 요약\n"
        "- 뉴스 첫 줄\n"
        "- 뉴스 둘째 줄\n"
        "- 뉴스 셋째 줄\n",
        encoding="utf-8",
    )
    settings = GmailSettings(
        sender="ssou56@gmail.com",
        recipient="recipient@example.com",
        credentials_path="credentials.json",
        timezone="Asia/Seoul",
    )

    draft = build_email_draft(newsletter_path, date(2026, 7, 2), settings)
    message = to_email_message(draft)
    html = message.get_body(("html",)).get_content()

    assert "text/html" in message.get_body(("html",)).get_content_type()
    assert "KOSPI 일일 리서치/뉴스레터" in html
    assert "뉴스 첫 줄" in html
    assert "newsletter-card" in html


def test_seconds_until_next_run_uses_next_day_after_1600():
    now = datetime(2026, 7, 2, 16, 1)

    seconds = seconds_until_next_run(now, hour=16, minute=0)

    assert seconds == timedelta(hours=23, minutes=59).total_seconds()

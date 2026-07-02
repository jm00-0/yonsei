from datetime import date

from src.run_daily_newsletter import main, run_daily_newsletter


def test_run_daily_newsletter_summarizes_writes_reports_and_sends_index(tmp_path):
    calls = []
    summaries = [{"stock": {"code": "005930", "name": "Samsung Electronics"}}]
    write_result = {
        "report_dir": tmp_path / "reports" / "2026-07-02",
        "index": tmp_path / "reports" / "2026-07-02" / "index.md",
        "details": [tmp_path / "reports" / "2026-07-02" / "005930-samsung-electronics.md"],
    }

    def summarize_func(report_date):
        calls.append(("summarize", report_date))
        return summaries

    def write_func(summary_data, report_date, output_root):
        calls.append(("write", summary_data, report_date, output_root))
        return write_result

    def send_func(index_path):
        calls.append(("send", index_path))
        return {
            "sender": "sender@example.com",
            "recipients": ["recipient@example.com"],
            "subject": "subject",
        }

    result = run_daily_newsletter(
        "2026-07-02",
        output_root=tmp_path / "reports",
        summarize_func=summarize_func,
        write_func=write_func,
        send_func=send_func,
    )

    assert calls == [
        ("summarize", "2026-07-02"),
        ("write", summaries, "2026-07-02", tmp_path / "reports"),
        ("send", write_result["index"]),
    ]
    assert result == {
        "date": "2026-07-02",
        "summaries": summaries,
        "reports": write_result,
        "email": {
            "sender": "sender@example.com",
            "recipients": ["recipient@example.com"],
            "subject": "subject",
        },
    }


def test_main_uses_cli_date_argument_when_present(tmp_path):
    calls = []

    def runner(report_date, output_root):
        calls.append((report_date, output_root))
        return {"date": report_date}

    result = main(
        ["2026-07-02", "--output-root", str(tmp_path / "custom-reports")],
        runner=runner,
    )

    assert calls == [("2026-07-02", tmp_path / "custom-reports")]
    assert result == {"date": "2026-07-02"}


def test_main_uses_today_when_date_argument_is_missing(tmp_path):
    calls = []

    def runner(report_date, output_root):
        calls.append((report_date, output_root))
        return {"date": report_date}

    result = main(
        ["--output-root", str(tmp_path / "reports")],
        runner=runner,
        today_func=lambda: date(2026, 7, 2),
    )

    assert calls == [("2026-07-02", tmp_path / "reports")]
    assert result == {"date": "2026-07-02"}

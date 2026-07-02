import argparse
from datetime import date
from pathlib import Path

from src.daily_summary_builder import summarize_daily_sources
from src.email_sender import send_gmail_newsletter
from src.report_writer import write_markdown_reports


def run_daily_newsletter(
    report_date,
    output_root="reports",
    summarize_func=summarize_daily_sources,
    write_func=write_markdown_reports,
    send_func=send_gmail_newsletter,
):
    summaries = summarize_func(report_date)
    reports = write_func(summaries, report_date, output_root)
    email_result = send_func(reports["index"])

    return {
        "date": report_date,
        "summaries": summaries,
        "reports": reports,
        "email": email_result,
    }


def main(argv=None, runner=run_daily_newsletter, today_func=date.today):
    args = _parse_args(argv)
    report_date = args.date or today_func().isoformat()
    return runner(report_date, Path(args.output_root))


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Generate and send the daily KOSPI stock newsletter.",
    )
    parser.add_argument(
        "date",
        nargs="?",
        help="Report date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--output-root",
        default="reports",
        help="Directory where markdown reports are written.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    main()

"""Main entrypoint for the KOSPI daily newsletter workflow."""

from __future__ import annotations

import argparse
import logging
import os
from datetime import date
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - python-dotenv is optional at runtime.
    load_dotenv = None

from .comments import fetch_comments_for_stock
from .gmail_sender import (
    GmailConfigError,
    build_email_draft,
    load_gmail_settings,
    write_draft_file,
)
from .kb_research import fetch_kb_research_for_stock
from .market_data import get_top_kospi_movers
from .markdown_writer import Newsletter, NewsletterEntry, write_newsletter
from .news import fetch_news_for_stock
from .scheduler import run_daily_scheduler
from .summarizer import collect_section

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure basic console logging."""

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def generate_newsletter(
    as_of: date | None = None,
    output_root: str | Path = "reports",
) -> Path:
    """Generate one daily newsletter and a reviewable Gmail draft file."""

    run_date = as_of or date.today()
    stocks = get_top_kospi_movers()
    entries: list[NewsletterEntry] = []

    for stock in stocks:
        entries.append(
            NewsletterEntry(
                stock=stock,
                research_summary=collect_section(lambda stock=stock: fetch_kb_research_for_stock(stock)),
                comment_summary=collect_section(lambda stock=stock: fetch_comments_for_stock(stock)),
                news_summary=collect_section(lambda stock=stock: fetch_news_for_stock(stock)),
            )
        )

    newsletter = Newsletter(as_of=run_date, entries=entries)
    newsletter_path = write_newsletter(newsletter, output_root=output_root)
    logger.info("Newsletter written to %s", newsletter_path)

    try:
        settings = load_gmail_settings()
    except GmailConfigError as exc:
        logger.warning("Gmail draft skipped: %s", exc)
        return newsletter_path

    draft = build_email_draft(newsletter_path, run_date, settings)
    draft_path = write_draft_file(draft, newsletter_path.parent)
    logger.info("Gmail draft written to %s", draft_path)
    return newsletter_path


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Generate the KOSPI daily newsletter.")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run every day at 16:00 KST. This creates files only and does not auto-send email.",
    )
    parser.add_argument(
        "--output-root",
        default="reports",
        help="Root folder for dated newsletter output.",
    )
    return parser.parse_args()


def main() -> None:
    """Run one newsletter job or start the scheduler."""

    if load_dotenv:
        load_dotenv()

    configure_logging()
    args = parse_args()

    if args.schedule:
        run_daily_scheduler(lambda: generate_newsletter(output_root=args.output_root))
        return

    generate_newsletter(output_root=args.output_root)


if __name__ == "__main__":
    main()

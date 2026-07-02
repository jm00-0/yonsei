"""Markdown newsletter rendering and writing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .market_data import StockMove


@dataclass(frozen=True)
class NewsletterEntry:
    """Newsletter content for one stock."""

    stock: StockMove
    research_summary: list[str]
    comment_summary: list[str]
    news_summary: list[str]


@dataclass(frozen=True)
class Newsletter:
    """Daily newsletter model."""

    as_of: date
    entries: list[NewsletterEntry]


def _render_lines(lines: list[str]) -> str:
    return "\n".join(f"- {line}" for line in lines)


def render_newsletter(newsletter: Newsletter) -> str:
    """Render a newsletter as Markdown."""

    lines = [
        f"# {newsletter.as_of.isoformat()} KOSPI 일일 리서치/뉴스레터",
        "",
        "대상: 장마감 후 등락률 절댓값 5% 이상 KOSPI 종목 중 상위 10개",
        "",
    ]

    if not newsletter.entries:
        lines.extend(["선정된 종목이 없습니다.", ""])
        return "\n".join(lines)

    for index, entry in enumerate(newsletter.entries, start=1):
        stock = entry.stock
        sign = "+" if stock.change_rate >= 0 else ""
        lines.extend(
            [
                f"## {index}. {stock.name} ({stock.symbol}) {sign}{stock.change_rate:.2f}%",
                "",
                "### 리서치 요약",
                _render_lines(entry.research_summary),
                "",
                "### 댓글/투자자 반응 요약",
                _render_lines(entry.comment_summary),
                "",
                "### 뉴스 요약",
                _render_lines(entry.news_summary),
                "",
            ]
        )

    return "\n".join(lines)


def write_newsletter(
    newsletter: Newsletter,
    output_root: str | Path = "reports",
) -> Path:
    """Write newsletter to reports/YYYY-MM-DD/newsletter.md."""

    output_dir = Path(output_root) / newsletter.as_of.isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "newsletter.md"
    output_path.write_text(render_newsletter(newsletter), encoding="utf-8")
    return output_path

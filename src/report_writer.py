import re
from pathlib import Path


SUMMARY_SECTIONS = (
    ("news", "News Summary"),
    ("comment", "Comment Summary"),
    ("research", "Research Summary"),
)


def write_markdown_reports(summaries, date, output_root="reports"):
    report_dir = Path(output_root) / date
    report_dir.mkdir(parents=True, exist_ok=True)

    detail_paths = []
    index_rows = []

    for item in summaries:
        stock = item["stock"]
        filename = build_report_filename(stock["code"], stock["name"])
        detail_path = report_dir / filename
        detail_path.write_text(
            build_stock_detail_markdown(item, date),
            encoding="utf-8",
        )

        detail_paths.append(detail_path)
        index_rows.append(_build_index_row(stock, filename))

    index_path = report_dir / "index.md"
    index_path.write_text(
        build_index_markdown(date, index_rows),
        encoding="utf-8",
    )

    return {
        "report_dir": report_dir,
        "index": index_path,
        "details": detail_paths,
    }


def build_report_filename(code, name):
    safe_code = str(code).zfill(6)
    safe_name = re.sub(r"[^0-9A-Za-z가-힣]+", "-", str(name).strip().lower())
    safe_name = re.sub(r"-+", "-", safe_name).strip("-")
    if not safe_name:
        safe_name = "stock"
    return f"{safe_code}-{safe_name}.md"


def build_index_markdown(date, rows):
    lines = [
        f"# {date} KOSPI Daily Report",
        "",
        "| Stock | Code | Change rate | Detail |",
        "| --- | --- | ---: | --- |",
        *rows,
        "",
    ]
    return "\n".join(lines)


def build_stock_detail_markdown(item, date):
    stock = item["stock"]
    lines = [
        f"# {stock['name']} ({str(stock['code']).zfill(6)})",
        "",
        f"- Date: {date}",
        f"- Market: {stock.get('market', 'KOSPI')}",
        f"- Change rate: {_format_change_rate(stock['change_rate'])}",
        "",
    ]

    for source_type, heading in SUMMARY_SECTIONS:
        lines.extend([f"## {heading}", ""])
        lines.extend(_numbered_lines(item.get("summaries", {}).get(source_type, [])))
        lines.append("")

    lines.extend(["## Reference Links", ""])
    reference_lines = _reference_lines(item.get("source_documents", []))
    lines.extend(reference_lines or ["- No reference links collected."])
    lines.append("")

    return "\n".join(lines)


def _build_index_row(stock, filename):
    return (
        f"| {stock['name']} | {str(stock['code']).zfill(6)} | "
        f"{_format_change_rate(stock['change_rate'])} | [details]({filename}) |"
    )


def _format_change_rate(change_rate):
    return f"{change_rate:+.2f}%"


def _numbered_lines(lines):
    padded_lines = list(lines[:3])
    while len(padded_lines) < 3:
        padded_lines.append("No summary line available.")
    return [f"{index}. {line}" for index, line in enumerate(padded_lines, start=1)]


def _reference_lines(documents):
    reference_lines = []
    seen_urls = set()
    for document in documents:
        url = document.get("url")
        title = document.get("title") or url
        source_type = document.get("source_type", "source")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        reference_lines.append(f"- [{title}]({url}) - {source_type}")
    return reference_lines

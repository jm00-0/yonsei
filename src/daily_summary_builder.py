import re
from html.parser import HTMLParser

from src.daily_source_collector import collect_daily_sources


SOURCE_TYPES = ("news", "comment", "research")
REASON_KEYWORDS = (
    "earnings",
    "guidance",
    "profit",
    "loss",
    "revenue",
    "forecast",
    "target",
    "foreign",
    "institution",
    "sell",
    "selling",
    "buy",
    "buying",
    "semiconductor",
    "memory",
    "demand",
    "supply",
    "policy",
    "rate",
    "exchange",
    "won",
    "decline",
    "fell",
    "fall",
    "drop",
    "rise",
    "rose",
    "jump",
    "surge",
    "concern",
    "risk",
)


def summarize_daily_sources(
    date,
    stock_api=None,
    list_html_fetcher=None,
    detail_html_fetcher=None,
    summarizer=None,
    threshold=5.0,
    limit=10,
    per_source_limit=3,
    lines_per_type=3,
):
    if detail_html_fetcher is None:
        detail_html_fetcher = _fetch_html
    if summarizer is None:
        summarizer = summarize_relevant_text

    daily_sources = collect_daily_sources(
        date,
        stock_api=stock_api,
        html_fetcher=list_html_fetcher,
        threshold=threshold,
        limit=limit,
        per_source_limit=per_source_limit,
    )

    return [
        _summarize_stock_sources(
            stock_sources,
            detail_html_fetcher,
            summarizer,
            lines_per_type,
        )
        for stock_sources in daily_sources
    ]


def summarize_relevant_text(stock, source_type, documents, lines_per_type=3):
    candidates = []
    for document in documents:
        text = document.get("text", "") or document.get("title", "")
        for sentence in _split_sentences(text):
            score = _score_sentence(sentence, stock)
            if score > 0:
                candidates.append((score, sentence))

    selected = []
    seen = set()
    for _, sentence in sorted(candidates, key=lambda item: item[0], reverse=True):
        normalized = sentence.casefold()
        if normalized in seen:
            continue
        selected.append(sentence)
        seen.add(normalized)
        if len(selected) == lines_per_type:
            break

    while len(selected) < lines_per_type:
        selected.append(f"No additional {source_type} reason text was found.")

    return selected


def extract_text_from_html(html):
    parser = _TextExtractor()
    parser.feed(html or "")
    return " ".join(" ".join(parser.parts).split())


def _summarize_stock_sources(
    stock_sources,
    detail_html_fetcher,
    summarizer,
    lines_per_type,
):
    documents = []
    for source in stock_sources["sources"]:
        html = detail_html_fetcher(source["url"])
        documents.append(
            {
                **source,
                "text": extract_text_from_html(html),
            }
        )

    summaries = {}
    for source_type in SOURCE_TYPES:
        typed_documents = [
            document
            for document in documents
            if document["source_type"] == source_type
        ]
        summaries[source_type] = summarizer(
            stock_sources["stock"],
            source_type,
            typed_documents,
            lines_per_type,
        )

    return {
        **stock_sources,
        "source_documents": documents,
        "summaries": summaries,
    }


def _score_sentence(sentence, stock):
    lowered = sentence.casefold()
    score = 0

    if stock.get("name", "").casefold() in lowered:
        score += 3
    if stock.get("code", "") in sentence:
        score += 2

    change_rate = stock.get("change_rate")
    if change_rate is not None:
        if str(abs(change_rate)).rstrip("0").rstrip(".") in sentence:
            score += 1
        if change_rate < 0 and any(
            word in lowered for word in ("fell", "fall", "drop", "decline", "selling")
        ):
            score += 2
        if change_rate > 0 and any(
            word in lowered for word in ("rose", "rise", "jump", "surge", "buying")
        ):
            score += 2

    score += sum(1 for keyword in REASON_KEYWORDS if keyword in lowered)
    return score


def _split_sentences(text):
    rough_sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [sentence.strip() for sentence in rough_sentences if sentence.strip()]


def _fetch_html(url):
    import requests

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._skip_depth += 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self.parts.append(text)

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1

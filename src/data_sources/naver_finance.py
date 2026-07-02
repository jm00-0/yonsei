from html.parser import HTMLParser
from urllib.parse import urljoin


NAVER_FINANCE_BASE_URL = "https://finance.naver.com"


def build_naver_finance_urls(code):
    stock_code = str(code).zfill(6)
    return {
        "main": f"{NAVER_FINANCE_BASE_URL}/item/main.naver?code={stock_code}",
        "news": f"{NAVER_FINANCE_BASE_URL}/item/news_news.naver?code={stock_code}&page=&clusterId=",
        "comment": f"{NAVER_FINANCE_BASE_URL}/item/board.naver?code={stock_code}",
        "research": (
            f"{NAVER_FINANCE_BASE_URL}/research/company_list.naver"
            f"?searchType=itemCode&itemCode={stock_code}"
        ),
    }


def parse_news_links(html, limit=None):
    return _parse_candidate_links(
        html,
        source_type="news",
        allowed_path_fragments=("news_read.naver",),
        limit=limit,
    )


def parse_comment_links(html, limit=None):
    return _parse_candidate_links(
        html,
        source_type="comment",
        allowed_path_fragments=("board_read.naver",),
        limit=limit,
    )


def parse_research_links(html, limit=None):
    return _parse_candidate_links(
        html,
        source_type="research",
        allowed_path_fragments=("company_read.naver",),
        base_url=f"{NAVER_FINANCE_BASE_URL}/research/",
        limit=limit,
    )


def collect_source_links_from_html(news_html="", comment_html="", research_html=""):
    return [
        *parse_news_links(news_html),
        *parse_comment_links(comment_html),
        *parse_research_links(research_html),
    ]


def _parse_candidate_links(
    html,
    source_type,
    allowed_path_fragments,
    base_url=NAVER_FINANCE_BASE_URL,
    limit=None,
):
    parser = _AnchorParser()
    parser.feed(html or "")

    links = []
    seen_urls = set()

    for anchor in parser.anchors:
        href = anchor["href"]
        title = _clean_text(anchor["text"])

        if not href or not title or href.startswith("#") or href.startswith("javascript:"):
            continue

        if not any(fragment in href for fragment in allowed_path_fragments):
            continue

        normalized_url = urljoin(base_url, href)
        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        links.append(
            {
                "title": title,
                "url": normalized_url,
                "source_type": source_type,
            }
        )

        if limit is not None and len(links) >= limit:
            break

    return links


def _clean_text(text):
    return " ".join(text.split())


class _AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = []
        self._current_anchor = None

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return

        href = dict(attrs).get("href", "")
        self._current_anchor = {"href": href, "text": ""}

    def handle_data(self, data):
        if self._current_anchor is not None:
            self._current_anchor["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._current_anchor is not None:
            self.anchors.append(self._current_anchor)
            self._current_anchor = None

"""Gmail newsletter draft helpers.

This module does not auto-send email. It prepares a reviewable email draft file
with both plain text and HTML newsletter content.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from email.message import EmailMessage
from html import escape
from pathlib import Path


class GmailConfigError(RuntimeError):
    """Raised when required Gmail environment settings are missing."""


@dataclass(frozen=True)
class GmailSettings:
    """Environment-based Gmail settings."""

    sender: str
    recipient: str
    credentials_path: str
    timezone: str


@dataclass(frozen=True)
class EmailDraft:
    """Prepared newsletter email content."""

    subject: str
    body: str
    html_body: str
    sender: str
    recipient: str


def load_gmail_settings(env: dict[str, str] | None = None) -> GmailSettings:
    """Load Gmail settings from environment variables."""

    values = env or os.environ
    sender = values.get("GMAIL_SENDER", "").strip()
    recipient = values.get("GMAIL_RECIPIENT", "").strip()
    credentials_path = values.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    timezone = values.get("TIMEZONE", "Asia/Seoul").strip() or "Asia/Seoul"

    missing = [
        name
        for name, value in (
            ("GMAIL_SENDER", sender),
            ("GMAIL_RECIPIENT", recipient),
            ("GOOGLE_APPLICATION_CREDENTIALS", credentials_path),
        )
        if not value
    ]
    if missing:
        raise GmailConfigError(f"Missing environment variables: {', '.join(missing)}")

    return GmailSettings(
        sender=sender,
        recipient=recipient,
        credentials_path=credentials_path,
        timezone=timezone,
    )


def build_email_draft(
    newsletter_path: str | Path,
    as_of: date,
    settings: GmailSettings,
) -> EmailDraft:
    """Build an email draft from a newsletter Markdown file."""

    body = Path(newsletter_path).read_text(encoding="utf-8")
    return EmailDraft(
        subject=f"[{as_of.isoformat()}] KOSPI 일일 리서치/뉴스레터",
        body=body,
        html_body=markdown_to_newsletter_html(body),
        sender=settings.sender,
        recipient=settings.recipient,
    )


def markdown_to_newsletter_html(markdown: str) -> str:
    """Convert the generated Markdown newsletter into simple email-safe HTML."""

    body_parts: list[str] = []
    list_items: list[str] = []

    def flush_list() -> None:
        if list_items:
            body_parts.append(
                '<ul class="newsletter-list">' + "".join(list_items) + "</ul>"
            )
            list_items.clear()

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            flush_list()
            continue

        if line.startswith("# "):
            flush_list()
            body_parts.append(f'<h1 class="newsletter-title">{escape(line[2:])}</h1>')
        elif line.startswith("## "):
            flush_list()
            body_parts.append(f'<section class="newsletter-card"><h2>{escape(line[3:])}</h2>')
        elif line.startswith("### "):
            flush_list()
            body_parts.append(f'<h3>{escape(line[4:])}</h3>')
        elif line.startswith("- "):
            list_items.append(f"<li>{escape(line[2:])}</li>")
        else:
            flush_list()
            body_parts.append(f"<p>{escape(line)}</p>")

    flush_list()
    html_body = "\n".join(body_parts).replace(
        '</ul>\n<section class="newsletter-card">',
        '</ul>\n</section>\n<section class="newsletter-card">',
    )
    if '<section class="newsletter-card">' in html_body:
        html_body += "\n</section>"

    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <style>
      body {{ margin: 0; padding: 0; background: #f4f6f8; color: #17202a; font-family: Arial, sans-serif; }}
      .newsletter-shell {{ max-width: 720px; margin: 0 auto; padding: 24px; }}
      .newsletter-title {{ margin: 0 0 16px; padding: 24px; background: #143d59; color: #ffffff; font-size: 24px; line-height: 1.35; }}
      .newsletter-card {{ margin: 16px 0; padding: 20px; background: #ffffff; border: 1px solid #d8dee4; }}
      h2 {{ margin: 0 0 14px; color: #143d59; font-size: 20px; }}
      h3 {{ margin: 18px 0 8px; color: #2f4858; font-size: 16px; }}
      p {{ margin: 0 0 12px; line-height: 1.6; }}
      .newsletter-list {{ margin: 0 0 8px; padding-left: 20px; }}
      .newsletter-list li {{ margin: 6px 0; line-height: 1.55; }}
    </style>
  </head>
  <body>
    <div class="newsletter-shell">
      {html_body}
    </div>
  </body>
</html>"""


def to_email_message(draft: EmailDraft) -> EmailMessage:
    """Convert a draft into a standard email message."""

    message = EmailMessage()
    message["From"] = draft.sender
    message["To"] = draft.recipient
    message["Subject"] = draft.subject
    message.set_content(draft.body)
    message.add_alternative(draft.html_body, subtype="html")
    return message


def write_draft_file(
    draft: EmailDraft,
    output_dir: str | Path,
    filename: str = "gmail_draft.eml",
) -> Path:
    """Write a reviewable email draft file without sending it."""

    path = Path(output_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_email_message(draft).as_string(), encoding="utf-8")
    return path

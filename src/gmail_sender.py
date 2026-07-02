"""Gmail newsletter draft helpers.

This module does not auto-send email. It prepares an email draft file so a
person can review it before sending, which keeps classroom runs safe.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from email.message import EmailMessage
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
        sender=settings.sender,
        recipient=settings.recipient,
    )


def to_email_message(draft: EmailDraft) -> EmailMessage:
    """Convert a draft into a standard email message."""

    message = EmailMessage()
    message["From"] = draft.sender
    message["To"] = draft.recipient
    message["Subject"] = draft.subject
    message.set_content(draft.body)
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

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587
SENDER_ENV = "GMAIL_SENDER"
PASSWORD_ENV = "GMAIL_APP_PASSWORD"
RECIPIENTS_ENV = "NEWSLETTER_RECIPIENTS"


def send_gmail_newsletter(index_path, env=None, smtp_factory=None, subject=None):
    env = os.environ if env is None else env
    smtp_factory = smtplib.SMTP if smtp_factory is None else smtp_factory

    sender = _require_env(env, SENDER_ENV)
    password = _require_env(env, PASSWORD_ENV)
    recipients = parse_recipients(_require_env(env, RECIPIENTS_ENV))
    if not recipients:
        raise ValueError(f"{RECIPIENTS_ENV} must contain at least one recipient")

    index_path = Path(index_path)
    body = index_path.read_text(encoding="utf-8")
    report_date = index_path.parent.name
    subject = subject or build_newsletter_subject(report_date)

    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)

    with smtp_factory(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(message)

    return {
        "sender": sender,
        "recipients": recipients,
        "subject": subject,
    }


def parse_recipients(raw_recipients):
    return [
        recipient.strip()
        for recipient in raw_recipients.split(",")
        if recipient.strip()
    ]


def build_newsletter_subject(report_date):
    return f"[Yonsei Stock Report] {report_date} KOSPI Daily Report"


def _require_env(env, name):
    value = env.get(name)
    if not value:
        raise ValueError(f"{name} environment variable is required")
    return value

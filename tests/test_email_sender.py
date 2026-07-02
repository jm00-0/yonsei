import pytest

from src.email_sender import (
    build_newsletter_subject,
    parse_recipients,
    send_gmail_newsletter,
)


class FakeSMTP:
    instances = []

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.started_tls = False
        self.login_calls = []
        self.sent_messages = []
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, sender, password):
        self.login_calls.append((sender, password))

    def send_message(self, message):
        self.sent_messages.append(message)


def test_parse_recipients_splits_commas_and_strips_empty_values():
    result = parse_recipients("one@example.com, two@example.com,, three@example.com ")

    assert result == ["one@example.com", "two@example.com", "three@example.com"]


def test_build_newsletter_subject_uses_report_date():
    result = build_newsletter_subject("2026-07-02")

    assert result == "[Yonsei Stock Report] 2026-07-02 KOSPI Daily Report"


def test_send_gmail_newsletter_reads_index_markdown_and_uses_env_values(tmp_path):
    report_dir = tmp_path / "reports" / "2026-07-02"
    report_dir.mkdir(parents=True)
    index_path = report_dir / "index.md"
    index_path.write_text("# Daily Report\n\n- Samsung summary", encoding="utf-8")
    env = {
        "GMAIL_SENDER": "sender@example.com",
        "GMAIL_APP_PASSWORD": "app-password",
        "NEWSLETTER_RECIPIENTS": "a@example.com,b@example.com",
    }
    FakeSMTP.instances = []

    result = send_gmail_newsletter(index_path, env=env, smtp_factory=FakeSMTP)

    smtp = FakeSMTP.instances[0]
    message = smtp.sent_messages[0]

    assert result == {
        "sender": "sender@example.com",
        "recipients": ["a@example.com", "b@example.com"],
        "subject": "[Yonsei Stock Report] 2026-07-02 KOSPI Daily Report",
    }
    assert (smtp.host, smtp.port) == ("smtp.gmail.com", 587)
    assert smtp.started_tls is True
    assert smtp.login_calls == [("sender@example.com", "app-password")]
    assert message["From"] == "sender@example.com"
    assert message["To"] == "a@example.com, b@example.com"
    assert message["Subject"] == "[Yonsei Stock Report] 2026-07-02 KOSPI Daily Report"
    assert message.get_content() == "# Daily Report\n\n- Samsung summary\n"


def test_send_gmail_newsletter_requires_secret_environment_values(tmp_path):
    index_path = tmp_path / "index.md"
    index_path.write_text("# Daily Report", encoding="utf-8")

    with pytest.raises(ValueError, match="GMAIL_SENDER"):
        send_gmail_newsletter(index_path, env={}, smtp_factory=FakeSMTP)

from pathlib import Path


WORKFLOW_PATH = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "daily-newsletter.yml"
)


def test_daily_newsletter_workflow_is_configured_for_kst_delivery():
    assert WORKFLOW_PATH.exists()

    content = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "cron: \"0 7 * * *\"" in content
    assert "workflow_dispatch:" in content
    assert "actions/checkout@v4" in content
    assert "actions/setup-python@v5" in content
    assert "pip install -r requirements.txt" in content
    assert "python -m src.run_daily_newsletter" in content
    assert "TZ: Asia/Seoul" in content


def test_daily_newsletter_workflow_reads_gmail_values_from_secrets():
    assert WORKFLOW_PATH.exists()

    content = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "GMAIL_SENDER: ${{ secrets.GMAIL_SENDER }}" in content
    assert "GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}" in content
    assert "NEWSLETTER_RECIPIENTS: ${{ secrets.NEWSLETTER_RECIPIENTS }}" in content
    assert "KRX_ID: ${{ secrets.KRX_ID }}" in content
    assert "KRX_PW: ${{ secrets.KRX_PW }}" in content

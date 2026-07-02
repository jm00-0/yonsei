"""Simple daily scheduler for 16:00 KST newsletter runs."""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

DEFAULT_TIMEZONE = "Asia/Seoul"


def seconds_until_next_run(
    now: datetime,
    hour: int = 16,
    minute: int = 0,
) -> float:
    """Return seconds until the next scheduled local run time."""

    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)

    return (target - now).total_seconds()


def run_daily_scheduler(
    action: Callable[[], object],
    timezone_name: str | None = None,
    hour: int = 16,
    minute: int = 0,
) -> None:
    """Run action every day at the configured KST time."""

    tz = ZoneInfo(timezone_name or os.getenv("TIMEZONE", DEFAULT_TIMEZONE))

    while True:
        now = datetime.now(tz)
        wait_seconds = seconds_until_next_run(now, hour=hour, minute=minute)
        logger.info("Next newsletter run in %.0f seconds", wait_seconds)
        time.sleep(wait_seconds)

        try:
            action()
        except Exception as exc:  # noqa: BLE001 - scheduler must continue after one failed run.
            logger.exception("Scheduled newsletter run failed: %s", exc)

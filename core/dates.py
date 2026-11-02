"""Date helpers. All of EcoBin's 'today' and 'this week' logic goes through here."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from core.config import APP_TIMEZONE


def today() -> date:
    return datetime.now(ZoneInfo(APP_TIMEZONE)).date()


def week_start(day: date) -> date:
    """Monday of the ISO week containing `day`."""
    return day - timedelta(days=day.weekday())


def week_key(day: date) -> str:
    """ISO week identifier such as '2026-W45'."""
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def period_key(period: str, day: date) -> str:
    if period == "daily":
        return day.isoformat()
    if period == "weekly":
        return week_key(day)
    raise ValueError(f"Unknown challenge period: {period}")

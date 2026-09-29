"""Pick the theme for a calendar day, counted in Tehran time."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from zoneinfo import ZoneInfo

TEHRAN = ZoneInfo("Asia/Tehran")
EPOCH = date(2026, 1, 1)


def today_in_tehran(now: datetime | None = None) -> date:
    """Today's date in Tehran. `now` must be timezone-aware when given."""
    return (now or datetime.now(TEHRAN)).astimezone(TEHRAN).date()


def theme_for(day: date, order: Sequence[str]) -> str:
    if not order:
        raise ValueError("theme order is empty")
    return order[(day - EPOCH).days % len(order)]


def theme_for_hour(now: datetime, order: Sequence[str]) -> str:
    """Rotate every hour instead of every day (`now` must be timezone-aware)."""
    if not order:
        raise ValueError("theme order is empty")
    start = datetime(EPOCH.year, EPOCH.month, EPOCH.day, tzinfo=TEHRAN)
    return order[int((now - start).total_seconds() // 3600) % len(order)]

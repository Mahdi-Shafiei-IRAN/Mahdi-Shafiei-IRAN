from datetime import date, datetime, timedelta, timezone

import pytest

from generator.rotation import EPOCH, TEHRAN, theme_for, theme_for_hour, today_in_tehran

ORDER = ("a", "b", "c", "d", "e", "f")


def test_epoch_is_first_theme_and_days_advance():
    assert theme_for(EPOCH, ORDER) == "a"
    assert theme_for(EPOCH + timedelta(days=1), ORDER) == "b"
    assert theme_for(EPOCH + timedelta(days=6), ORDER) == "a"
    assert theme_for(date(2025, 12, 31), ORDER) == "f"


def test_every_theme_shows_once_per_cycle():
    cycle = [theme_for(EPOCH + timedelta(days=i), ORDER) for i in range(100, 106)]
    assert sorted(cycle) == sorted(ORDER)


def test_empty_order_is_rejected():
    with pytest.raises(ValueError):
        theme_for(EPOCH, ())


def test_day_flips_at_tehran_midnight():
    # Tehran is UTC+3:30, so midnight there is 20:30 UTC
    assert today_in_tehran(datetime(2026, 9, 28, 20, 29, tzinfo=timezone.utc)) == date(2026, 9, 28)
    assert today_in_tehran(datetime(2026, 9, 28, 20, 31, tzinfo=timezone.utc)) == date(2026, 9, 29)


def test_hourly_rotation_advances_every_hour():
    start = datetime(2026, 1, 1, 0, 30, tzinfo=TEHRAN)
    assert [theme_for_hour(start + timedelta(hours=h), ORDER) for h in range(7)] == list(ORDER) + ["a"]

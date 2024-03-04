"""Module to manage time related calculations."""

import os
from datetime import datetime, timedelta
from pytz import timezone


DEFAULT_TIMEDELTA = 15 * 60  # 15 minutes
default_timezone_str = os.getenv("TZ", "Europe/Madrid")


def current_timestamp() -> int:
    """Return current timestamp."""
    return int(current_datetime().timestamp())
    # return int(time.time())


# def current_timestamp_with_timedelta(delta_in_seconds: int = DEFAULT_TIMEDELTA) -> int:
#     """Return current timestamp plus a timedelta."""
#     return current_timestamp() + delta_in_seconds


def current_datetime(time_zone_str=default_timezone_str) -> datetime:
    """Generate current datetime for given timezone."""
    time_zone = timezone(time_zone_str)
    return datetime.now(time_zone)


def datetime_from_timestamp(timestamp, time_zone_str=default_timezone_str) -> datetime:
    """Return datetime for the given timestamp."""
    time_zone = timezone(time_zone_str)
    return datetime.fromtimestamp(timestamp, tz=time_zone)


def current_datetime_with_timedelta(
    time_zone=default_timezone_str,
    days: float = 0,
    seconds: float = 0,
    microseconds: float = 0,
    milliseconds: float = 0,
    minutes: float = 0,
    hours: float = 0,
    weeks: float = 0,
) -> datetime:
    """Get current datetime plus a timedelta."""
    ret_datetime = current_datetime(time_zone) + timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    )
    return ret_datetime


def current_timestamp_with_timedelta(
    time_zone=default_timezone_str,
    days: float = 0,
    seconds: float = 0,
    microseconds: float = 0,
    milliseconds: float = 0,
    minutes: float = 0,
    hours: float = 0,
    weeks: float = 0,
) -> int:
    """Get current timestamp plus a timedelta."""
    ret_datetime = current_datetime_with_timedelta(
        time_zone=time_zone,
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    )
    return int(ret_datetime.timestamp())

from datetime import datetime, timedelta
from typing import Any


def get_session_end(session: dict[str, Any]) -> datetime | None:
    started_at = session.get("started_at")
    duration = session.get("duration")
    if not started_at or duration is None:
        return None
    try:
        started_at_dt = datetime.fromisoformat(started_at)
        return started_at_dt + timedelta(minutes=duration)
    except ValueError:
        return None


def remaining_time_text(end_time: datetime | None) -> str:
    if not end_time:
        return "00:00"

    remaining = end_time - datetime.utcnow()
    if remaining.total_seconds() <= 0:
        return "00:00"

    total_seconds = int(remaining.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def session_end_from_data(session: dict[str, Any]) -> datetime | None:
    return get_session_end(session)

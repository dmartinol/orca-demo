"""Aggregate normalised events into a small report summary."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any, Iterable

ERROR_LEVELS = ("error", "fatal")


def summarize(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Return counts and the covered time window for ``events``.

    The returned mapping is the stable contract shared by every renderer:

    ``total``          number of events
    ``errors``         number of ``error`` + ``fatal`` events
    ``by_level``       ``{level: count}``, sorted by level
    ``by_service``     ``{service: count}``, sorted by service
    ``first_ts``       ISO-8601 UTC string or ``None``
    ``last_ts``        ISO-8601 UTC string or ``None``
    ``window_seconds`` seconds between first and last event (0 when empty)
    """
    events = list(events)
    by_level = Counter(event["level"] for event in events)
    by_service = Counter(event["service"] for event in events)
    timestamps = [event["ts"] for event in events]
    first = min(timestamps) if timestamps else None
    last = max(timestamps) if timestamps else None

    return {
        "total": len(events),
        "errors": sum(by_level[level] for level in ERROR_LEVELS),
        "by_level": dict(sorted(by_level.items())),
        "by_service": dict(sorted(by_service.items())),
        "first_ts": _iso(first),
        "last_ts": _iso(last),
        "window_seconds": int((last - first).total_seconds()) if first and last else 0,
    }


def _iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None

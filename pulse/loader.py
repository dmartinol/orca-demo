"""Load and validate Pulse event log files."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ("ts", "level", "service", "message")


class EventError(ValueError):
    """Raised when an event line cannot be parsed."""


def parse_timestamp(value: Any) -> datetime:
    """Parse an ISO-8601 timestamp and return it as an aware UTC datetime."""
    if not isinstance(value, str):
        raise EventError(f"invalid timestamp: {value!r}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EventError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_event(line: str, *, line_number: int | None = None) -> dict[str, Any]:
    """Parse one JSON-lines event, normalising ``ts`` and ``level``."""
    where = f" (line {line_number})" if line_number is not None else ""
    try:
        record = json.loads(line)
    except json.JSONDecodeError as exc:
        raise EventError(f"invalid JSON{where}: {exc.msg}") from exc
    if not isinstance(record, dict):
        raise EventError(f"event must be a JSON object{where}")

    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        raise EventError(f"missing field(s): {', '.join(missing)}{where}")

    event = dict(record)
    for field in ("level", "service", "message"):
        if not isinstance(event[field], str):
            raise EventError(f"{field} must be a string{where}")

    event["ts"] = parse_timestamp(event["ts"])
    event["level"] = event["level"].lower()
    return event


def load_events(path: str | Path) -> list[dict[str, Any]]:
    """Read a JSON-lines event file and return normalised events.

    Blank lines are ignored. Events keep file order; ``ts`` becomes an aware UTC
    ``datetime`` and ``level`` is lowercased.
    """
    events: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            events.append(parse_event(line, line_number=number))
    return events

"""Render a plain-text report."""

from __future__ import annotations

from typing import Any


def render_text(summary: dict[str, Any]) -> str:
    """Render ``summary`` as a compact fixed-width text report."""
    lines = ["PULSE REPORT", "=" * 12]
    if not summary["total"]:
        lines.append("No events.")
        return "\n".join(lines)

    lines.append(f"Events: {summary['total']}  Errors: {summary['errors']}")
    lines.append(
        f"Window: {summary['first_ts']} -> {summary['last_ts']} "
        f"({summary['window_seconds']}s)"
    )
    lines.append("")
    lines.append("By level:")
    for level, count in summary["by_level"].items():
        lines.append(f"  {level:<6} {count}")
    lines.append("By service:")
    for service, count in summary["by_service"].items():
        lines.append(f"  {service:<12} {count}")
    return "\n".join(lines)

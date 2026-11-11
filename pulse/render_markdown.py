"""Render a summary as a Markdown report."""

from __future__ import annotations

import re
from typing import Any


def _escape_cell(value: Any) -> str:
    """Escape untrusted values for use in a Markdown table cell."""
    escaped = str(value).replace("|", r"\|")
    return re.sub(r"[\r\n]+", " ", escaped)


def _render_table(heading: str, first_column: str, values: dict[Any, Any]) -> list[str]:
    lines = [
        f"## {heading}",
        "",
        f"| {first_column} | Count |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| {_escape_cell(name)} | {_escape_cell(count)} |"
        for name, count in values.items()
    )
    return lines


def render_markdown(summary: dict[str, Any]) -> str:
    """Render ``summary`` as a readable Markdown report."""
    lines = ["# Pulse report", ""]
    if not summary["total"]:
        lines.append("No events recorded.")
        return "\n".join(lines)

    lines.append(
        f"Events: {_escape_cell(summary['total'])}  "
        f"Errors: {_escape_cell(summary['errors'])}  "
        f"Window: {_escape_cell(summary['window_seconds'])}s"
    )
    lines.append("")
    lines.extend(_render_table("By level", "Level", summary["by_level"]))
    lines.append("")
    lines.extend(_render_table("By service", "Service", summary["by_service"]))
    return "\n".join(lines)

"""Render a summary as pretty-printed JSON."""

from __future__ import annotations

import json
from typing import Any


def render_json(summary: dict[str, Any]) -> str:
    """Render ``summary`` as indented JSON."""
    return json.dumps(summary, indent=2)

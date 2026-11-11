"""Command line entry point for Pulse."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .loader import EventError, load_events
from .render import render_text
from .render_json import render_json
from .render_markdown import render_markdown
from .summarize import summarize

# Renderers are registered here. Feature work adds entries; the integration
# task wires filters and the markdown/html renderers into this table.
FORMATS = {
    "text": render_text,
    "json": render_json,
    "markdown": render_markdown,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pulse", description="Summarise incident event logs."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    report = sub.add_parser("report", help="summarise an event log file")
    report.add_argument("path", help="path to a JSON-lines event file")
    report.add_argument("--format", choices=sorted(FORMATS), default="text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "report":
        try:
            events = load_events(args.path)
        except OSError as exc:
            print(f"pulse: cannot read {args.path}: {exc.strerror}", file=sys.stderr)
            return 2
        except EventError as exc:
            print(f"pulse: {exc}", file=sys.stderr)
            return 2

        summary = summarize(events)
        print(FORMATS[args.format](summary))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

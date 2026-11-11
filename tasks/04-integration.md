# Task 04 — Wire filters and renderers into the CLI

You are the **integration worker**. The parallel feature branches (filters,
Markdown renderer, HTML renderer) are already merged into your base. Your job is
to compose them behind the CLI without changing their public APIs.

## Goal

Extend `pulse/cli.py` so `pulse report` supports filtering and output formats, and
add `tests/test_cli_formats.py`.

## Files you own

Edit only:

- `pulse/cli.py`
- create `tests/test_cli_formats.py`

Do **not** edit `pulse/filters.py`, `pulse/render_markdown.py`,
`pulse/render_html.py`, `pulse/loader.py`, `pulse/summarize.py`,
`pulse/render.py`, or any existing test. If a dependency's API does not match its
spec, report the mismatch instead of changing it.

## Available APIs

```python
from .filters import filter_events, parse_window   # task 01
from .render_markdown import render_markdown       # task 02
from .render_html import render_html               # task 03
```

`summary` is the dict from `pulse.summarize.summarize`. `parse_window` accepts
`90s`, `15m`, `2h`, `7d` and raises `ValueError` otherwise. `filter_events`
accepts `since=<datetime>`, `levels=<iterable[str]>`, `services=<iterable[str>]`.

## Required behaviour

1. `pulse report FILE [--format text|markdown|html]`, default `text`.
2. Filters, all optional and combinable:
   - `--window 2h` — relative to the **last event timestamp** in the file
     (`since = max(event["ts"]) - parse_window(value)`). An empty file means no
     filtering.
   - `--level error` — repeatable; values are matched case-insensitively.
   - `--service api` — repeatable; values are matched case-insensitively.
3. Pipeline order: load → compute `since` (if `--window`) → `filter_events(...)` →
   `summarize(...)` → renderer for `--format`.
4. Error handling: an invalid `--window` (for example `--window 2x`) prints
   `pulse: ...` to stderr and exits `2`; it must not raise a traceback. Keep the
   existing behaviour for unreadable/malformed files.
5. Keep `FORMATS` as the single registry of renderers; extend it rather than
   branching on format strings at the call site.
6. Keep every existing public function and CLI flag working unchanged.

## Tests (`tests/test_cli_formats.py`, unittest only)

- `--format markdown` and `--format html` succeed and contain the expected
  markers (`# Pulse report`, `<section class="pulse-report">`).
- `--window` keeps only recent events (build a temp log with timestamps far
  apart and assert the total).
- `--level` / `--service` filter, including repeated flags and case-insensitivity.
- Invalid window returns `2` and writes to stderr.
- The default format is still `text`.

## Definition of done

1. `python3 -m unittest discover -s tests -t .` — **all** tests pass (existing and
   new).
2. These commands run successfully:
   - `python3 -m pulse report data/sample_events.jsonl --format markdown`
   - `python3 -m pulse report data/sample_events.jsonl --format html`
   - `python3 -m pulse report data/sample_events.jsonl --window 5m --level error --service api`

Report: summary of the change, commands run, and the full test result line.

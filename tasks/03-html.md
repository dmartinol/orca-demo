# Task 03 — HTML renderer

You are one of three independent workers building features for **Pulse**, a small
dependency-free Python CLI that summarises incident event logs. Other workers are
editing different files at the same time.

## Goal

Create a new module `pulse/render_html.py` plus tests in
`tests/test_render_html.py`.

## Files you own

Create only:

- `pulse/render_html.py`
- `tests/test_render_html.py`

Do **not** edit `pulse/cli.py`, `pulse/render.py`, `pulse/summarize.py`,
`pulse/loader.py`, existing tests, `Makefile`, or `docs/`. The coordinator wires
your renderer into the CLI in a later task.

## Input contract

Same `summary` dict documented in `tasks/02-markdown.md` (total, errors, by_level,
by_service, first_ts, last_ts, window_seconds). Values are untrusted strings.

## API contract (exact name and signature)

```python
def render_html(summary: dict) -> str:
    ...
```

Output requirements:

- Returns a self-contained HTML **fragment** (no `<html>`/`<head>`/`<body>`, no
  external CSS or JS) that starts with `<section class="pulse-report">` and ends
  with `</section>`.
- Contains `<h2>Pulse report</h2>`.
- Contains a `<p class="pulse-summary">` with total, errors, and window seconds.
- Contains two `<table>` elements with `<caption>` (`By level`, `By service`) and
  header cells `Level`/`Count`, `Service`/`Count`.
- Each level row carries `class="pulse-level pulse-level--<level>"` where
  `<level>` is the lowercased level; each service row carries
  `class="pulse-service"`.
- **Escape every interpolated value** with `html.escape(..., quote=True)`; table
  cells must never contain raw `<`, `>`, `&`, `"`, or `'` from input.
- When `total == 0`, render `<p class="pulse-empty">No events recorded.</p>` and
  no tables.
- Pure function: no I/O, no printing. Standard library only.

## Tests

Use `unittest` only. Cover: structure and counts for a full summary, empty
summary, escaping (service name like `<script>alert("x")</script>` must not appear
unescaped), and the severity class on level rows.

## Definition of done

1. `python3 -m unittest discover -s tests -t .` passes from the repo root.
2. `python3 -m unittest tests.test_render_html -v` passes.

Report: files created, the test command you ran, and its final result line.

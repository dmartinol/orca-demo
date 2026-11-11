# Task 02 — Markdown renderer

You are one of three independent workers building features for **Pulse**, a small
dependency-free Python CLI that summarises incident event logs. Other workers are
editing different files at the same time.

## Goal

Create a new module `pulse/render_markdown.py` plus tests in
`tests/test_render_markdown.py`.

## Files you own

Create only:

- `pulse/render_markdown.py`
- `tests/test_render_markdown.py`

Do **not** edit `pulse/cli.py`, `pulse/render.py`, `pulse/summarize.py`,
`pulse/loader.py`, existing tests, `Makefile`, or `docs/`. The coordinator wires
your renderer into the CLI in a later task.

## Input contract

`summary` is a plain `dict` produced by `pulse.summarize.summarize`:

```python
{
    "total": 20,
    "errors": 4,
    "by_level": {"debug": 1, "error": 3, "fatal": 1, "info": 11, "warn": 4},
    "by_service": {"api": 8, "db": 7, "worker": 5},
    "first_ts": "2026-11-11T09:00:00Z",  # or None
    "last_ts": "2026-11-11T09:16:22Z",   # or None
    "window_seconds": 982,               # 0 when empty
}
```

Dict ordering is already sorted; preserve it.

## API contract (exact name and signature)

```python
def render_markdown(summary: dict) -> str:
    ...
```

Output requirements:

- Starts with `# Pulse report`.
- One summary line containing the total, error count, and window duration, e.g.
  `**20 events**, **4 errors**, window **982s**.`
- A `## By level` section with a two-column Markdown table (`Level`, `Count`).
- A `## By service` section with a two-column Markdown table (`Service`, `Count`).
- Every value interpolated into a table cell must escape `|` as `\|` and collapse
  newlines to spaces. (Service names come from log files and are untrusted.)
- When `total == 0`, output the heading plus `No events recorded.` and no tables.
- Ends with a single newline.
- Pure function: no I/O, no printing, no globals mutated. Standard library only.

## Tests

Use `unittest` only. Cover: full summary (assert headings, table rows, counts,
summary line), empty summary, and escaping of a service name containing `|` and a
newline.

## Definition of done

1. `python3 -m unittest discover -s tests -t .` passes from the repo root.
2. `python3 -m unittest tests.test_render_markdown -v` passes.

Report: files created, the test command you ran, and its final result line.

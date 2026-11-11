# Task 01 — Time, level, and service filters

You are one of three independent workers building features for **Pulse**, a small
dependency-free Python CLI that summarises incident event logs. Other workers are
editing different files at the same time.

## Goal

Create a new module `pulse/filters.py` plus tests in `tests/test_filters.py`.

## Files you own

Create only:

- `pulse/filters.py`
- `tests/test_filters.py`

Do **not** edit `pulse/cli.py`, `pulse/render.py`, `pulse/summarize.py`,
`pulse/loader.py`, existing tests, `Makefile`, or `docs/`. The coordinator wires
your module into the CLI in a later task.

## Context you can rely on

`pulse.loader.load_events(path)` returns a list of events shaped like:

```python
{"ts": datetime(...), "level": "error", "service": "api", "message": "..."}
```

`ts` is always an aware UTC `datetime`; `level` is always lowercase. Events keep
file order. Python 3.11, standard library only.

## API contract (exact names and signatures)

```python
def parse_window(text: str) -> datetime.timedelta:
    ...

def filter_events(
    events: list[dict],
    *,
    since: datetime | None = None,
    levels: Iterable[str] | None = None,
    services: Iterable[str] | None = None,
) -> list[dict]:
    ...
```

`parse_window`:

- Accepts a positive integer followed by a unit suffix: `s`, `m`, `h`, `d`
  (for example `"90s"`, `"15m"`, `"2h"`, `"7d"`).
- Case-insensitive and tolerant of surrounding whitespace (`" 2H "` works).
- Returns a `datetime.timedelta`.
- Raises `ValueError` for anything else, including empty input, a missing unit,
  an unknown unit, a non-integer value, and zero or negative values.

`filter_events`:

- Returns a **new list**; never mutates the input events or the input lists.
- Preserves the original order.
- `since`: include events whose `ts >= since`. `None` means no time constraint.
  Assume `since` is timezone-aware; if it is naive, treat it as UTC instead of
  raising.
- `levels` / `services`: case-insensitive exact matches. `None` means "no
  constraint"; an empty iterable means "match nothing". Deduplicate internally
  if convenient — behaviour must be unaffected.
- Filters combine with AND.

## Tests

Use `unittest` only (no pytest, no third-party packages). Cover at minimum:

- every unit suffix and a mixed-case/whitespace input;
- invalid windows (empty, `"15"`, `"15x"`, `"-1m"`, `"0s"`, `"1.5h"`);
- `since` boundary is inclusive; naive `since` treated as UTC;
- level and service filters, case-insensitivity;
- `None` vs empty-list semantics;
- input list is not mutated and order is preserved.

## Definition of done

1. `python3 -m unittest discover -s tests -t .` passes from the repo root.
2. `python3 -m unittest tests.test_filters -v` passes.
3. Your module imports nothing outside the standard library and does not import
   other `pulse` modules.

Report: files created, the test command you ran, and its final result line.

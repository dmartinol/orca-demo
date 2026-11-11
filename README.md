# Pulse

Pulse is a deliberately tiny incident-report CLI. It parses JSON-lines event
logs, summarizes them — event counts, error totals, time window — and renders
a report. Plain text today; the renderer registry leaves room for more formats.

## Quick start

```bash
make test     # 20 tests, stdlib only, no install step
make report   # text report over data/sample_events.jsonl
```

Requires Python 3.11+ — standard library only, nothing to install.

## Usage

```bash
python3 -m pulse report data/sample_events.jsonl [--format text]
```

```text
PULSE REPORT
============
Events: 20  Errors: 4
Window: 2026-11-11T09:00:00Z -> 2026-11-11T09:16:22Z (982s)

By level:
  debug  1
  error  3
  fatal  1
  info   11
  warn   4
By service:
  api          8
  db           7
  worker       5
```

Renderers register in the `FORMATS` table in `pulse/cli.py`; `text` is the only
one in `main`.

## Design notes

- **No dependencies.** Standard library only: `unittest`, `argparse`, `json`,
  `html`.
- **Stable contract.** `summarize()` returns one documented dict; renderers are
  written against it, so a new format can be added without touching the rest.
- **Untrusted input.** Event logs are treated as hostile: escaping is an explicit
  review item.
- **Deterministic.** Windows are computed from the last event in the file, never
  from wall-clock time, so output is reproducible.
- **Small on purpose.** Every module fits on a screen and the suite runs in
  milliseconds.

## Orchestration demo

This repo doubles as an Orca orchestration demo: one agent implements a GitHub
issue in its own worktree, a second agent reviews the PR it opens. Start with
**AGENTS.md** (repo map and demo commands) or the full
**[runbook](docs/demo-script.md)**.

## License

MIT

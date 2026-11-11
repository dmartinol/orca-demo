# Pulse — an Orca orchestration demo

Pulse is a deliberately tiny incident-report CLI. It exists to make **Orca's
orchestration model** visible: one coordinator, several agents, isolated
worktrees, a real dependency graph, and verification you can watch happen.

The app is small on purpose. The interesting diff is the *process*.

```text
                     ┌──────────────────────┐
                     │  Coordinator (you)   │
                     └──────────┬───────────┘
        worker-start            │            worker_done / questions
      ┌─────────────┬───────────┴───────────┬──────────────┐
      ▼             ▼                       ▼              ▼
  filters        markdown                 html          review
  (codex)        (claude)                 (codex)       (claude)
  worktree A     worktree B               worktree C    worktree E
      └─────────────┴───────────┬───────────┴──────────────┘
                                ▼
                     merge → integrate → verify
                            (worktree D)
```

## What it demonstrates

- **Parallel agents in isolated worktrees** — three feature workers, three real
  git checkouts, three branches, no shared files.
- **A dependency graph** — the integration task joins the three features and owns
  the only shared file (`pulse/cli.py`).
- **Live steering** — message a running worker, answer a worker's question, gate
  a task on a human decision.
- **Cross-agent review** — a Claude worker reviews work produced by Codex
  workers, and must cite `file:line` evidence.
- **Proof, not vibes** — every worker's "done" includes a green `make test`;
  the coordinator re-runs the suite before the final merge.

## Quick start

```bash
make test     # 20 tests, stdlib only, no install step
make report   # text report over data/sample_events.jsonl
```

Requires Python 3.11+ (standard library only) and the Orca app (the
orchestration demo drives it through the `orca` CLI).

## Repo map

| Path | What it is |
| --- | --- |
| `pulse/loader.py` | Parse and validate JSON-lines events. |
| `pulse/summarize.py` | Counts, error totals, time window. |
| `pulse/render.py` | Plain-text renderer (the only one in `main`). |
| `pulse/cli.py` | `pulse report FILE [--format ...]`. |
| `tests/` | `unittest` suite, fast enough to run live. |
| `data/sample_events.jsonl` | 20 realistic events across `api`, `db`, `worker`. |
| `tasks/` | **The demo.** Self-contained worker specs with file ownership. |
| `docs/demo-script.md` | Minute-by-minute runbook with copy-paste commands. |
| `docs/orchestration-101.md` | Run / Task / Dispatch / Gate vocabulary and the loop. |

## The conflict-free design

Each worker owns a disjoint set of files. That is the whole trick, and it is
encoded in the specs, not in a convention people have to remember:

| Spec | Owns | Depends on |
| --- | --- | --- |
| `tasks/01-filters.md` | `pulse/filters.py`, `tests/test_filters.py` | — |
| `tasks/02-markdown.md` | `pulse/render_markdown.py`, `tests/test_render_markdown.py` | — |
| `tasks/03-html.md` | `pulse/render_html.py`, `tests/test_render_html.py` | — |
| `tasks/04-integration.md` | `pulse/cli.py`, `tests/test_cli_formats.py` | 01, 02, 03 |
| `tasks/05-review.md` | `docs/review-notes.md` (read-only review) | 04 |

## Run the demo

```bash
# one-time
orca repo add --path "$PWD" --json
orca repo set-base-ref --repo id:<REPO_ID> --ref main

# fan out (then end your turn — Orca wakes you on worker_done)
orca orchestration worker-start --spec-file tasks/01-filters.md \
  --worktree new-top-level --repo id:<REPO_ID> --name filters --agent codex
```

The full runbook, talking points, gate/steer steps, payoff commands, and reset
instructions are in **[docs/demo-script.md](docs/demo-script.md)**.

## Design notes

- **No dependencies.** Stdlib `unittest`, `argparse`, `json`, `html`. Nothing to
  install while an audience watches.
- **Stable contract.** `summarize()` returns one documented dict; every renderer
  and the filter module are specced against it, so independently written modules
  compose without negotiation.
- **Untrusted input.** Event logs are treated as hostile: escaping is an explicit
  review item for both HTML and Markdown.
- **Deterministic.** Relative windows are computed from the last event in the
  file, never from wall-clock time, so demo output is reproducible.

## License

MIT

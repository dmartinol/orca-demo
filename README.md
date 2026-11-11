# Pulse — an Orca orchestration demo

Pulse is a deliberately tiny incident-report CLI. It exists to make one Orca
workflow visible end to end: **one agent implements a GitHub issue, a second agent
reviews the pull request it opens.**

```text
  issue #1            worker A: implementer                 worker B: reviewer
  (the spec)  ──────▶ (codex · Luna 5.6 high, worktree) ───▶ PR ──▶ (opencode · Luna 6 xhigh)
                                                                    │
                                                                    ▼
                                                          review posted on the PR
```

Two agents, one real handoff artifact, and each one launched natively with its
own model.

## What it demonstrates

- **The issue is the spec.** The worker reads acceptance criteria with `gh issue
  view`, implements, tests, pushes, and opens a PR that closes the issue.
- **Isolation without ceremony.** The implementer gets its own Orca worktree and
  branch; `main` is never touched by the worker.
- **Native launches, explicit models.** Each worker is one `worker-start` with
  `--agent` and `--model`: the implementer is Codex on `gpt-5.6-luna` (effort
  high); the reviewer is OpenCode on `gpt-6-luna#xhigh`, pinned by the repo's
  `opencode.json`.
- **The PR is the handoff.** The reviewer starts in the same checkout after the
  PR exists — no copying files, no re-explaining context.
- **A different agent reviews.** The reviewer checks the issue's criteria against
  the diff, runs the tests, and posts an approve / comment / request-changes
  review on GitHub.
- **A loop if needed.** A "request changes" review can be sent back to the
  implementer, who pushes to the same branch and the reviewer re-checks.

## Quick start

```bash
make test     # 20 tests, stdlib only, no install step
make report   # text report over data/sample_events.jsonl
```

Requires Python 3.11+ (standard library only), the Orca app, an authenticated
`gh` CLI, `codex`, and `opencode`.

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

## Repo map

| Path | What it is |
| --- | --- |
| `pulse/loader.py` | Parse and validate JSON-lines events. |
| `pulse/summarize.py` | Counts, error totals, time window. |
| `pulse/render.py` | Plain-text renderer (the only one in `main`). |
| `pulse/cli.py` | `pulse report FILE [--format ...]`. |
| `tests/` | `unittest` suite, fast enough to run live. |
| `data/sample_events.jsonl` | 20 realistic events across `api`, `db`, `worker`. |
| `AGENTS.md` | Instructions for coding agents: commands, style, traps. |
| `opencode.json` | Pins the reviewer's OpenCode model: `openai/gpt-6-luna#xhigh`. |
| `tasks/01-implement-issue.md` | Workflow for the implementer. |
| `tasks/02-review-pr.md` | Workflow and checklist for the reviewer. |
| `docs/demo-script.md` | 6-minute runbook with copy-paste commands. |
| `docs/orchestration-101.md` | Run / Task / Dispatch vocabulary and the loop. |

## Run the demo

Issue **#1** (Markdown output format) is the canned target.

Commands use `--repo name:orca-demo`: the repo must be registered in Orca under
the display name `orca-demo`, which is what `orca repo add --path .` records from
the folder name. If your folder or name differs, use `--repo path:<abs path>` or
the id from `orca repo list --json`.

**Implement** — new worktree, Codex on Luna 5.6 (high):

```bash
orca orchestration worker-start \
  --spec "Read tasks/01-implement-issue.md and implement issue #1. Open a PR when green." \
  --task-title "Implement issue #1" \
  --agent codex --model gpt-5.6-luna --effort high \
  --worktree new-top-level --name issue-1 --repo name:orca-demo --json
```

**Review** — same checkout, OpenCode on Luna 6 (xhigh):

```bash
orca orchestration worker-start \
  --spec "Read tasks/02-review-pr.md and review PR #<PR> against issue #1." \
  --task-title "Review PR #<PR>" \
  --agent opencode2 \
  --worktree name:issue-1 --json
```

Full runbook, talking points, the fix loop, and reset steps:
**[docs/demo-script.md](docs/demo-script.md)**.

> The reviewer's model is not on the command line: Orca's `--effort` does not
> apply to OpenCode, so `opencode.json` at the repo root pins
> `openai/gpt-6-luna#xhigh` for it. A project config overrides your global
> OpenCode default inside this repo; merge it to the base ref before creating
> the demo worktree.

## Design notes

- **No dependencies.** Stdlib `unittest`, `argparse`, `json`, `html`. Nothing to
  install while an audience watches.
- **Stable contract.** `summarize()` returns one documented dict; renderers are
  written against it, so a worker can add one without touching the rest.
- **Untrusted input.** Event logs are treated as hostile: escaping is an explicit
  review item.
- **Deterministic.** Windows are computed from the last event in the file, never
  from wall-clock time, so demo output is reproducible.
- **Small on purpose.** Every module fits on a screen and the suite runs in
  milliseconds, so the audience can follow the diff and the verification live.

## License

MIT

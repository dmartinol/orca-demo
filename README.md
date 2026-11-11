# Pulse — an Orca orchestration demo

Pulse is a deliberately tiny incident-report CLI. It exists to make one Orca
workflow visible end to end: **one agent implements a GitHub issue, a second agent
reviews the pull request it opens.**

```text
  issue #1            worker A: implementer                 worker B: reviewer
  (the spec)  ──────▶ (codex, own worktree + branch) ──▶ PR ──▶ (claude, same checkout)
                                                              │
                                                              ▼
                                                    review posted on the PR
```

No task graph, no gates, no merges to orchestrate. Just two agents and a real
handoff artifact.

## What it demonstrates

- **The issue is the spec.** The worker reads acceptance criteria with `gh issue
  view`, implements, tests, pushes, and opens a PR that closes the issue.
- **Isolation without ceremony.** The implementer gets its own Orca worktree and
  branch; `main` is never touched by the worker.
- **The PR is the handoff.** The reviewer starts in the same checkout after the
  PR exists — no copying files, no re-explaining context.
- **A different agent reviews.** Reviewer runs a different model, checks the
  issue's criteria against the diff, runs the tests, and posts an approve /
  comment / request-changes review on GitHub.
- **A loop if needed.** A "request changes" review can be sent back to the
  implementer, who pushes to the same branch and the reviewer re-checks.

## Quick start

```bash
make test     # 20 tests, stdlib only, no install step
make report   # text report over data/sample_events.jsonl
```

Requires Python 3.11+ (standard library only), the Orca app, and an authenticated
`gh` CLI for the demo.

## Repo map

| Path | What it is |
| --- | --- |
| `pulse/loader.py` | Parse and validate JSON-lines events. |
| `pulse/summarize.py` | Counts, error totals, time window. |
| `pulse/render.py` | Plain-text renderer (the only one in `main`). |
| `pulse/cli.py` | `pulse report FILE [--format ...]`. |
| `tests/` | `unittest` suite, fast enough to run live. |
| `data/sample_events.jsonl` | 20 realistic events across `api`, `db`, `worker`. |
| `tasks/01-implement-issue.md` | Workflow for the implementer. |
| `tasks/02-review-pr.md` | Workflow and checklist for the reviewer. |
| `docs/demo-script.md` | 6-minute runbook with copy-paste commands. |
| `docs/orchestration-101.md` | Run / Task / Dispatch vocabulary and the loop. |

## Run the demo

Issue **#1** (Markdown output format) is the canned target:

```bash
# 1. implement: new worktree, own branch, opens a PR
orca orchestration worker-start \
  --spec "Read tasks/01-implement-issue.md and implement issue #1. Open a PR when green." \
  --task-title "Implement issue #1" \
  --worktree new-top-level --repo id:<REPO_ID> --name issue-1 --agent codex

# 2. review: same checkout, different agent, posts a review on the PR
orca orchestration worker-start \
  --spec "Read tasks/02-review-pr.md and review PR #<PR> against issue #1." \
  --task-title "Review PR #<PR>" \
  --worktree name:issue-1 --agent claude
```

Full runbook, talking points, the fix loop, and reset steps:
**[docs/demo-script.md](docs/demo-script.md)**.

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

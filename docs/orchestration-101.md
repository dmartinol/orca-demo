# Orca orchestration in one page

Orca runs coding agents in **isolated git worktrees** and lets one agent (the
**coordinator**) hand work to others and collect the results. This repo uses the
smallest useful shape: an implementer and a reviewer.

```text
                 ┌─────────────────────┐
                 │ Coordinator (agent) │
                 └──────────┬──────────┘
        worker-start        │        ▲  worker_done / question
                 ┌──────────┴──────────┐
                 ▼                     ▼
         worker A: implement      worker B: review
         codex · Luna 5.6 high    opencode · Luna 6 xhigh
         own worktree+branch      same checkout
                 │                     ▲
                 └──── PR on GitHub ───┘
```

## Vocabulary

| Term | What it is |
| --- | --- |
| **Run** | A namespace and inbox for one objective. Created implicitly by the first `worker-start`, or explicitly with `orca orchestration run-create`. |
| **Task** | A unit of work with a spec and a status. `worker-start --spec` creates one. |
| **Dispatch** | The assignment of a Task to a specific agent terminal. Its id is how you message or inspect the worker. |
| **Worker** | The agent process doing a Task. It reports with `worker_done`, or asks with `ask` and waits. |
| **Worktree** | A real `git worktree`: its own checkout and branch. Workers cannot step on each other's files. |
| **Gate** | A decision that blocks a Task until a human resolves it. Optional; not used in the basic flow. |
| **Message** | Subject/body mail between agents: steering a live worker, answering a question, reporting. |

## Two ways to launch a worker

| Way | Command | When |
| --- | --- | --- |
| **Native** | `worker-start --agent codex --model gpt-5.6-luna --effort high` | The default: one command, Orca launches the agent. This demo's way. |
| **Attach** | `terminal create --command "<exact argv>"` → `terminal wait --for tui-idle` → `worker-start --terminal <handle>` | You need flags Orca does not expose, e.g. a custom `codex --profile`. |

Attaching is not a hack: Orca supervises an agent terminal it did not start, and
everything after that — mail, `worker-show`, `worker-read`, gates — behaves
identically.

## The two-worker loop

1. **Create the handoff artifact first.** Here: a GitHub issue whose body is the
   spec (acceptance criteria + constraints).
2. **Start the coordinator with one prompt.** An agent in an Orca chat reads
   `tasks/00-run-demo.md`: it creates a Run, an implementer task, and a reviewer
   task blocked on it with `--deps`, then starts the implementer —
   `worker-start --agent codex --model gpt-5.6-luna --effort high --worktree
   new-top-level --name issue-1`.
3. **The coordinator ends its turn.** Orca wakes it on `worker_done`, `question`,
   or `escalation`. Polling is unnecessary and can consume the mail before Orca
   can deliver it.
4. **The reviewer starts when the implementer's task completes** — the dep turns
   ready and the coordinator runs `worker-start --agent opencode2 --worktree
   name:issue-1` in the same checkout; the repo's `opencode.json` pins its model
   to `openai/gpt-6-luna#xhigh`.
5. **Read the artifact, not the chat.** The PR and its review are the source of
   truth; the worker's report is the index.
6. **Loop if needed.** The coordinator `send`s the review back to the
   implementer; it pushes to the same branch and reports, and a re-review
   follows. The human hears the outcome at the end.

## Why the same worktree for review

The implementer's checkout is already on the PR branch, with the index and build
state warm. Starting the reviewer there means zero setup and no chance of
reviewing a stale copy. The reviewer is read-only by spec, so sharing is safe.

The alternative — a second worktree on `--base-branch <pr-branch>` — is useful
when you want the reviewer to be provably independent of the implementer's
working tree.

## Command cheat sheet

```bash
# discover
orca status --json
orca repo list --json
orca worktree list
orca worktree ps
orca orchestration task-list

# the demo's DAG (what tasks/00-run-demo.md drives)
orca orchestration run-create --objective "Implement and review issue #1" --json
orca orchestration task-create \
  --spec "Read tasks/01-implement-issue.md and implement issue #1." \
  --task-title "Implement issue #1" --json          # -> <IMPL_TASK>
orca orchestration task-create \
  --spec "Read tasks/02-review-pr.md and review the open PR that closes issue #1." \
  --task-title "Review the PR for issue #1" --deps '["<IMPL_TASK>"]' --json
orca orchestration worker-start --task <IMPL_TASK> \
  --agent codex --model gpt-5.6-luna --effort high \
  --worktree new-top-level --repo name:orca-demo --name issue-1
# on the wake after the implementer completes:
orca orchestration worker-start --task <REVIEW_TASK> \
  --agent opencode2 --worktree name:issue-1

# one task, no DAG (the --spec shortcut)
orca orchestration worker-start --agent codex --model gpt-5.6-luna --effort high \
  --spec "Read tasks/01-implement-issue.md and implement issue #1." \
  --worktree new-top-level --repo name:orca-demo --name issue-1

# implement (attach a terminal with an exact command, when you need custom argv)
orca worktree create --name issue-1 --repo name:orca-demo --no-parent --json
orca terminal create --worktree name:issue-1 \
  --command "codex --profile <name>" --json
orca terminal wait --terminal <HANDLE> --for tui-idle --timeout-ms 60000 --json
orca orchestration worker-start --spec "..." --terminal <HANDLE> --worktree name:issue-1

# observe and steer
orca orchestration task-list --ready --brief
orca orchestration worker-show --dispatch <DISPATCH_ID>
orca orchestration worker-read --dispatch <DISPATCH_ID> --limit 20
orca orchestration send --to dispatch:<DISPATCH_ID> \
  --subject "Review feedback" --body "Address the findings on PR #<PR>."

# optional gate
orca orchestration gate-create --task <TASK_ID> \
  --question "Approve merge?" --options '["approve","hold"]'
orca orchestration gate-resolve --id <GATE_ID> --resolution "approve"
```

## Failure modes worth showing

- **A spec gap** — the worker asks a clarifying question. Answer with `reply`;
  no restart needed.
- **A bad direction** — steer a running worker with `send`; it receives the
  message when its current turn ends.
- **Failing tests** — a `worker_done` that reports failing tests is not done.
  Send the fix back to the same worker, same branch.
- **A review you disagree with** — reply on the PR, not in chat. The PR is the
  durable record.

## Why this repo is small on purpose

The demo is about the **handoff**, not the product. Every module fits on a screen,
has no dependencies, and the suite runs in milliseconds, so the audience can
follow the diff and the verification live.

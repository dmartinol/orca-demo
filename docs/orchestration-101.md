# Orca orchestration in one page

Orca runs coding agents in **isolated git worktrees**, and lets one agent (the
**coordinator**) hand work to several others and collect the results. This repo is
shaped so that story is visible in `git log`, in the worktree list, and in the
code itself.

```text
                          ┌───────────────────────┐
                          │  Coordinator (you)    │
                          │  one Orca chat        │
                          └───────┬───────────────┘
             worker-start         │        ▲  worker_done / question
        ┌──────────────┬──────────┴────┬───┴───────────┐
        ▼              ▼               ▼               ▼
  worktree filters  worktree md    worktree html   worktree review
  agent: codex      agent: claude  agent: codex    agent: claude
  own branch        own branch     own branch      own branch
        └──────────────┴──────────┬────┴───────────────┘
                                  ▼
                        merge + integrate + verify
```

## Vocabulary

| Term | What it is |
| --- | --- |
| **Run** | A namespace and inbox for one objective. Created implicitly by the first `worker-start`, or explicitly with `orca orchestration run-create`. |
| **Task** | A unit of work with a spec and a status. `worker-start --spec` creates one. |
| **Dispatch** | The assignment of a Task to a specific agent terminal. Its id is how you message or inspect the worker. |
| **Worker** | The agent process doing a Task. It reports with `worker_done`, or asks with `ask` and waits. |
| **Worktree** | A real `git worktree`: its own checkout and branch. Workers cannot step on each other's files. |
| **Gate** | A decision that blocks a Task until a human (or coordinator) resolves it. |
| **Message** | Subject/body mail between agents: steering a live worker, answering a question, reporting. |

## The coordinator loop

1. **Create** a Run for the objective (`run-create`), or let the first worker create it.
2. **Start every independent worker** (`worker-start --worktree new-top-level --repo id:<id> --name <short> --agent <agent>`).
3. **End your turn.** This is the important part: Orca wakes the coordinator when a
   worker finishes, asks a question, or escalates. Polling is both unnecessary and
   discouraged — a polling script can consume the mail before Orca can deliver it.
4. **React.** Answer questions with `reply`, steer with `send`, then wait again.
5. **Integrate.** Merge the worker branches, start the next Task in the DAG (for
   example the CLI integration), verify.
6. **Report** to the human per Task: outcome, evidence, blockers.

## The worker side

A worker gets a **self-contained spec** — goal, constraints, files it may edit, and
the evidence that proves it is done. When finished it sends `worker_done` with an
outcome; when blocked it sends `ask` and parks until answered.

That is why the specs in `tasks/` are explicit about file ownership: three workers
writing three disjoint sets of files merge cleanly. The one shared file
(`pulse/cli.py`) is deliberately assigned to a fourth, dependent Task.

## Command cheat sheet

```bash
# discover
orca status --json
orca repo list --json
orca worktree list
orca worktree ps
orca orchestration run-list
orca orchestration task-list
orca orchestration gate-list

# start work
orca orchestration worker-start --spec-file tasks/01-filters.md \
  --worktree new-top-level --repo id:<REPO_ID> --name filters --agent codex

# observe and steer
orca orchestration worker-show --dispatch <DISPATCH_ID>
orca orchestration worker-read --dispatch <DISPATCH_ID> --limit 20
orca orchestration send --to dispatch:<DISPATCH_ID> \
  --subject "Question" --body "Keep the public API exactly as specced."

# gates
orca orchestration gate-create --task <TASK_ID> --question "Merge and integrate?" \
  --options '["merge","hold"]'
orca orchestration gate-resolve --id <GATE_ID> --resolution "merge"
```

## Failure modes worth showing

- **A spec gap** — a worker asks a clarifying question mid-flight. Answer with
  `reply`; no restart needed.
- **A bad direction** — steer a running worker with `send`; it receives the
  message when its current turn ends.
- **A merge conflict** — deliberately absent here, because file ownership is
  disjoint. That is a design property, not luck.
- **A failed check** — a `worker_done` that reports failing tests is not done;
  send the fix back to the same worker.

## Why this repo is small on purpose

The demo is about the **coordination**, not the product. Every module fits in a
screen, has no dependencies, and has tests that run in milliseconds, so the whole
audience can follow the diff and the verification live.

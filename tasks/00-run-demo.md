# Run the demo: implement an issue, review its PR

You are the **coordinator** of an Orca Run. The user names an issue number
(default **#1**). Two workers do all the work — an implementer (Codex) and a
reviewer (OpenCode) — and the PR on GitHub is the handoff between them. You
create the tasks, start the workers, relay, and report. You never edit the
checkout yourself.

Load your rulebook first — `orca skills get orchestration` — and treat it as
binding together with this brief: the skill carries the wake-loop discipline
(end your turn, never poll, `reply` semantics, escalation handling); this brief
carries the demo's exact commands.

## Once, at the start

Create the Run, the implementer task, and start the implementer in its own
worktree:

```bash
orca orchestration run-create --objective "Implement and review issue #<N>" --json

orca orchestration task-create \
  --spec "Read tasks/01-implement-issue.md and implement issue #<N>. Open a PR when green." \
  --task-title "Implement issue #<N>" --json
# -> <IMPL_TASK>

orca orchestration worker-start --task <IMPL_TASK> \
  --agent codex --model gpt-5.6-luna --effort high \
  --worktree new-top-level --name issue-<N> --repo name:orca-demo --json
```

Create the reviewer task **blocked on the implementer**. Its spec is
self-sufficient — the reviewer finds the PR from its checkout, so there is no
number to relay:

```bash
orca orchestration task-create \
  --spec "Read tasks/02-review-pr.md and review the open PR that closes issue #<N>." \
  --task-title "Review the PR for issue #<N>" \
  --deps '["<IMPL_TASK>"]' --json
# -> <REVIEW_TASK>
```

Then **end your turn**. Orca wakes you on `worker_done`, `question`, or
`escalation`.

## On every wake

- **A worker question** — answer it with
  `orca orchestration reply --id <message_id> --body "<answer>"` when the answer
  follows from the issue or the specs; otherwise ask the user first.
- **Ready tasks** — start every task that
  `orca orchestration task-list --ready --brief` lists. The reviewer task turns
  ready only after the implementer's task completes; start it in the
  implementer's checkout:

  ```bash
  orca orchestration worker-start --task <REVIEW_TASK> \
    --agent opencode2 --worktree name:issue-<N> --json
  ```

  No `--model` here: the repo's `opencode.json` pins `openai/gpt-6-luna#xhigh`.
- **A `worker_done` that reports failure is not done.** Send the report back to
  the same worker (`orca orchestration send --to dispatch:<dispatch_id>
  --subject "Retry" --body "<what failed and what to do>"`) or tell the user.
- **A review that requests changes is not the end.** Send the findings to the
  implementer the same way; when it reports a new push, create a fresh
  re-review task and start it in the same worktree.
- **Every task completed** — report to the user: PR URL, review verdict, top
  findings, issue link. Do not merge or close anything.

## Rules

- Never poll or run watch scripts; Orca wakes you. End your turn after every
  batch of actions.
- Never edit the workers' checkout; never push to `main`, merge, or close the PR.
- The PR and its review on GitHub are the source of truth; worker reports are
  the index.
- If you juggle more than one Run, pass `--run <RUN_ID>` explicitly.

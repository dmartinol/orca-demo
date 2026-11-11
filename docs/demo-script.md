# Live demo script (about 6 minutes)

**The pitch:** "I give one prompt. A coordinator agent runs the whole thing:
Codex implements issue #1 in its own worktree and opens a PR; OpenCode reviews
it against the issue's acceptance criteria; I get a report with the PR and its
review. Orca does the relay — I never wait, copy, or paste."

Everything below is copy-pasteable. `<PR>` comes from the coordinator's report
(or `gh pr list --state open`); the task and dispatch ids are printed by the
command that precedes them.

> The coordinator must be an Orca agent chat — any agent — so Orca can bind the
> Run and wake it. The watching commands work from any Orca-managed terminal.

---

## 0. Setup (once)

```bash
gh auth status                                  # needs repo scope
orca status --json                              # runtime is up
orca repo list --json                           # confirm "orca-demo" is listed
orca repo set-base-ref --repo name:orca-demo --ref main
make test                                       # 20 tests green
```

**Assumption — `orca-demo` is the Orca display name.** `orca repo add --path .`
derives that name from the folder, so this checkout must be registered as
`orca-demo`. A clone in `~/code/demo` is registered as `demo`, and every
`--repo name:orca-demo` below would fail. If yours differs, either re-register
the folder or replace `--repo name:orca-demo` with `--repo path:/abs/path` (or
the id from `orca repo list --json`).

Check the launch environment **from an Orca terminal** (not this sandbox):

```bash
codex --version                                 # implementer CLI
opencode --version                              # reviewer CLI
git show main:opencode.json                     # reviewer model pinned on the base ref
```

Both agents use their standard setup — no extra keys or profiles. The reviewer's
model (`openai/gpt-6-luna#xhigh`) is pinned by `opencode.json` in the repo root,
so it must be on the branch the demo worktree is created from: merge this repo's
changes to `main` (the base ref set below) before running the demo.

The canned target is **issue #1**, "Add a Markdown output format to pulse
report". Its acceptance criteria are the spec. To use another issue, substitute
its number below.

---

## 1. Baseline (30 s)

```bash
make report
```

Say: *"20 events, 4 errors. One text renderer. The issue asks for a Markdown
format, with escaping and an empty-state rule — small, but enough to review."*

---

## 2. One prompt: start the coordinator (2 min)

Open an agent chat in this repo — any agent, in the main checkout — and say:

> Read `tasks/00-run-demo.md` and run it for issue #1.

End of human involvement. The coordinator creates the Run, the implementer
task, and a reviewer task blocked on it, starts the implementer, and ends its
turn. Watch it live:

```bash
orca worktree ps
orca orchestration task-list
git log --oneline --graph --all --decorate
```

Say: *"One prompt. The coordinator owns the relay from here — Orca wakes it on
`worker_done`, it starts the reviewer, and it reports back. New worktree, new
branch, `main` untouched until a human merges."*

The implementer's report names a branch, a commit sha, and a **PR URL**; the PR
body must contain `Closes #1` and the test evidence.

---

## 3. Under the hood: what the coordinator runs (2 min)

For the audience, narrate the commands from `tasks/00-run-demo.md` — this is
what the agent you prompted is doing:

```bash
orca orchestration run-create --objective "Implement and review issue #1" --json

orca orchestration task-create \
  --spec "Read tasks/01-implement-issue.md and implement issue #1. Open a PR when green." \
  --task-title "Implement issue #1" --json
# -> <IMPL_TASK>

orca orchestration worker-start --task <IMPL_TASK> \
  --agent codex --model gpt-5.6-luna --effort high \
  --worktree new-top-level --name issue-1 --repo name:orca-demo --json

orca orchestration task-create \
  --spec "Read tasks/02-review-pr.md and review the open PR that closes issue #1." \
  --task-title "Review the PR for issue #1" \
  --deps '["<IMPL_TASK>"]' --json
```

Then the coordinator ends its turn. On the implementer's `worker_done` the
review task turns ready, and the coordinator starts it in the same checkout:

```bash
orca orchestration task-list --ready --brief
orca orchestration worker-start --task <REVIEW_TASK> \
  --agent opencode2 --worktree name:issue-1 --json
```

No `--model` for the reviewer — Orca's `--effort` does not apply to OpenCode, so
`opencode.json` in the repo root pins `openai/gpt-6-luna#xhigh`. And no PR
number is relayed: the reviewer is already on the PR branch, so `gh pr view`
resolves it.

Say: *"The handoff is the PR, not a copied folder — and the sequencing is
`--deps`, not a human with a clipboard. The reviewer reads the diff, runs the
same tests, and checks the issue's criteria — not its own taste."*

While the reviewer works:

```bash
orca orchestration worker-read --dispatch <REVIEW_DISPATCH_ID> --limit 20
gh pr view <PR> --json title,state,reviewDecision,statusCheckRollup
```

The payoff:

```bash
gh pr view <PR> --comments
gh pr diff <PR>
```

A review now exists on the PR: approved, commented, or changes requested, with
`file:line` findings. The coordinator reports this to the user and settles.

---

## 4. Optional: the fix loop (2 min)

If the review requested changes, the coordinator handles it — same worker, same
branch. It sends the findings back:

```bash
orca orchestration send \
  --to dispatch:<IMPLEMENTER_DISPATCH_ID> \
  --subject "Review feedback on the PR for issue #1" \
  --body "Address the findings in the PR review, push to the same branch, and report the new commit sha."
```

When the implementer reports, the coordinator creates and starts a re-review
task in the same worktree:

```bash
orca orchestration task-create \
  --spec "Read tasks/02-review-pr.md and re-review the open PR for issue #1. The implementer pushed fixes." \
  --task-title "Re-review the PR for issue #1" --json

orca orchestration worker-start --task <REREVIEW_TASK> \
  --agent opencode2 --worktree name:issue-1 --json
```

Say: *"The loop is coordinator messages and another review. No new worktree, no
lost context, no human relay."*

---

## 5. Wrap (30 s)

```bash
gh pr view <PR> --json state,reviewDecision,statusCheckRollup
git log --oneline --graph --all --decorate
orca worktree ps
```

Say: *"One prompt in: issue to PR to review, two different agents, one isolated
branch, and every claim backed by a test run."*

---

## Reset between demos

```bash
gh pr close <PR> --delete-branch        # or merge it, then reset main
orca worktree rm --worktree name:issue-1 --delete-branch

git switch main
git reset --hard origin/main
git clean -fd
```

Do not reset a repo with work you care about. Issue #1 stays open for the next
run; close or reopen it as needed (`gh issue close 1` / `gh issue reopen 1`).

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `runtime_access_denied` | Sandboxed shell. Run from an Orca terminal, or re-run with escalation. Never run `orca open` to fix this. |
| Reviewer uses the wrong model | `opencode.json` at the repo root pins `openai/gpt-6-luna#xhigh`; it must be on the branch being reviewed. Check `git show <branch>:opencode.json`. |
| Codex rejects the model | Run `codex --model gpt-5.6-luna` once in an Orca terminal to see the provider error, and check you are signed in (`codex login status`). |
| Worker cannot use `gh` | Check `gh auth status` in the same terminal: the agent inherits that environment. |
| `worker-start` exits non-zero | Read `failedStage`; check `orca worktree list` for a half-created worktree. Do not re-run blindly. |
| Worker never reports | Someone is polling. The coordinator must end its turn; Orca wakes it on `worker_done`, `question`, or `escalation`. |
| PR number unknown | It is in the implementer's `worker_done`; or `gh pr list --state open`. |
| Reviewer starts on the wrong code | `--worktree name:issue-1` must name the implementer's worktree. Check `orca worktree list`. |

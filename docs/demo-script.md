# Live demo script (about 6 minutes)

**The pitch:** "One agent takes a GitHub issue, implements it in its own
worktree with Codex on `gpt-5.6-luna`, and opens a PR. A second agent —
OpenCode on `gpt-6-luna` — reviews that PR against the issue's acceptance
criteria and posts the review."

Everything below is copy-pasteable. `<PR>` and the dispatch ids
are printed by the command that precedes them.

> Run from an Orca agent chat or Orca-managed terminal so Orca binds the Run to
> your coordinator. From an external shell, pass `--from <terminal-handle>` (see
> `orca terminal list --json`).

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

## 2. Implement with Codex (2 min)

One command: new worktree, new branch, Codex on Luna 5.6 at high effort,
supervised as an orchestration worker.

```bash
orca orchestration worker-start \
  --spec "Read tasks/01-implement-issue.md and implement issue #1. Open a PR when green." \
  --task-title "Implement issue #1" \
  --agent codex --model gpt-5.6-luna --effort high \
  --worktree new-top-level --name issue-1 --repo name:orca-demo --json
```

**Then end your turn.** Orca wakes you on `worker_done`. While it works:

```bash
orca worktree ps
orca orchestration task-list
git log --oneline --graph --all --decorate
```

Say: *"New worktree, new branch, Codex on Luna 5.6 at high effort. `main` is
untouched until a human merges the PR."*

The worker reports a branch, a commit sha, and a **PR URL**. The PR body must
contain `Closes #1` and the test evidence — that is the definition of done.

---

## 3. Review with OpenCode (2 min)

Same checkout, different agent, still one command. The model is not on the
command line — Orca's `--effort` does not apply to OpenCode — so `opencode.json`
in the repo root pins `openai/gpt-6-luna#xhigh`:

```bash
orca orchestration worker-start \
  --spec "Read tasks/02-review-pr.md and review PR #<PR> against issue #1." \
  --task-title "Review PR #<PR>" \
  --agent opencode2 \
  --worktree name:issue-1 --json
```

Say: *"The handoff is the PR, not a copied folder. The reviewer reads the diff,
runs the same tests, and checks the issue's criteria — not its own taste."*

While it works:

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
`file:line` findings.

---

## 4. Optional: the fix loop (2 min)

If the review requested changes, send it back — same worker, same branch:

```bash
orca orchestration send \
  --to dispatch:<IMPLEMENTER_DISPATCH_ID> \
  --subject "Review feedback on PR #<PR>" \
  --body "Address the findings in the PR review, push to the same branch, and report the new commit sha."
```

When it reports, start a fresh review with the same one-liner:

```bash
orca orchestration worker-start \
  --spec "Read tasks/02-review-pr.md and re-review PR #<PR> for issue #1. The implementer pushed fixes." \
  --task-title "Re-review PR #<PR>" \
  --agent opencode2 \
  --worktree name:issue-1 --json
```

Say: *"The loop is just messages and another review. No new worktree, no lost
context."*

---

## 5. Wrap (30 s)

```bash
gh pr view <PR> --json state,reviewDecision,statusCheckRollup
git log --oneline --graph --all --decorate
orca worktree ps
```

Say: *"Issue to PR to review, two different agents, one isolated branch, and
every claim backed by a test run."*

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
| Worker never reports | You are polling. End your turn; Orca wakes you on `worker_done`, `question`, or `escalation`. |
| PR number unknown | It is in the implementer's `worker_done`; or `gh pr list --state open`. |
| Reviewer starts on the wrong code | `--worktree name:issue-1` must name the implementer's worktree. Check `orca worktree list`. |

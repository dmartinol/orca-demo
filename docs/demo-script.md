# Live demo script (about 6 minutes)

**The pitch:** "One agent takes a GitHub issue, implements it in its own
worktree with `codex --profile enmaas`, and opens a PR. A second agent —
`opencode --standalone` — reviews that PR against the issue's acceptance criteria
and posts the review."

Everything below is copy-pasteable. `<PR>`, `<IMPL_TERM>`, and `<REVIEW_TERM>`
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
ls ~/.codex/enmaas.config.toml                  # profile exists
echo "${ENMAAS_KEY:+ENMAAS_KEY is set}"
opencode --version
```

`ENMAAS_KEY` must be visible to the process Orca spawns for the terminal. If it
is only in your interactive shell, put it in your shell profile (Orca terminals
are login shells) or launch Orca from a shell that has it.

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

## 2. Implement with `codex --profile enmaas` (2 min)

Orca's `--agent` launch takes no extra argv, so create the worktree and the agent
terminal yourself, then attach the orchestration task to that terminal.

```bash
# 2a. isolated checkout + branch
orca worktree create --name issue-1 --repo name:orca-demo --no-parent --json

# 2b. launch the exact CLI you want
orca terminal create --worktree name:issue-1 --title "implement #1" \
  --command "codex --profile enmaas -m rits/deepseek-ai/DeepSeek-V4.1-Flash-1017" --json
# -> <IMPL_TERM>

# 2c. wait for the TUI to be ready
orca terminal wait --terminal <IMPL_TERM> --for tui-idle --timeout-ms 60000 --json

# 2d. supervise it as an orchestration worker
orca orchestration worker-start \
  --spec "Read tasks/01-implement-issue.md and implement issue #1. Open a PR when green." \
  --task-title "Implement issue #1" \
  --terminal <IMPL_TERM> --worktree name:issue-1 --json
```

**Then end your turn.** Orca wakes you on `worker_done`. While it works:

```bash
orca worktree ps
orca orchestration task-list
git log --oneline --graph --all --decorate
```

Say: *"New worktree, new branch, my exact Codex profile. `main` is untouched
until a human merges the PR."*

The worker reports a branch, a commit sha, and a **PR URL**. The PR body must
contain `Closes #1` and the test evidence — that is the definition of done.

---

## 3. Review with `opencode --standalone` (2 min)

Same checkout, different agent, one extra flag:

```bash
orca terminal create --worktree name:issue-1 --title "review PR #<PR>" \
  --command "opencode --standalone" --json
# -> <REVIEW_TERM>

orca terminal wait --terminal <REVIEW_TERM> --for tui-idle --timeout-ms 60000 --json

orca orchestration worker-start \
  --spec "Read tasks/02-review-pr.md and review PR #<PR> against issue #1." \
  --task-title "Review PR #<PR>" \
  --terminal <REVIEW_TERM> --worktree name:issue-1 --json
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

When it reports, review the new push in a fresh OpenCode terminal:

```bash
orca terminal create --worktree name:issue-1 --title "re-review PR #<PR>" \
  --command "opencode --standalone" --json
# -> <REVIEW_TERM_2>
orca terminal wait --terminal <REVIEW_TERM_2> --for tui-idle --timeout-ms 60000 --json
orca orchestration worker-start \
  --spec "Read tasks/02-review-pr.md and re-review PR #<PR> for issue #1. The implementer pushed fixes." \
  --task-title "Re-review PR #<PR>" \
  --terminal <REVIEW_TERM_2> --worktree name:issue-1 --json
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
| Agent terminal never reaches idle | `orca terminal read --terminal <TERM> --limit 40`. Usually a missing `ENMAAS_KEY`, an unknown profile, or an opencode config problem. |
| `codex --profile enmaas` fails | `codex --profile enmaas --version` in an Orca terminal; the profile lives at `~/.codex/enmaas.config.toml`. |
| opencode uses the wrong model | The TUI takes its model from opencode's config, not argv. Point it at `rits/zai-org/glm-5-3` in your opencode config. |
| Worker cannot use `gh` | Check `gh auth status` in the same terminal: the agent inherits that environment. |
| `worker-start` exits non-zero | Read `failedStage`; check `orca worktree list` for a half-created worktree. Do not re-run blindly. |
| Worker never reports | You are polling. End your turn; Orca wakes you on `worker_done`, `question`, or `escalation`. |
| PR number unknown | It is in the implementer's `worker_done`; or `gh pr list --state open`. |
| Reviewer starts on the wrong code | `--worktree name:issue-1` must name the implementer's worktree. Check `orca worktree list`. |

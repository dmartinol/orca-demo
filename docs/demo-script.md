# Live demo script (about 12 minutes)

**The pitch:** "One coordinator, five agents, five isolated worktrees, one
integrated result. This is a real incident dashboard — small enough to read, real
enough to test."

Everything below is copy-pasteable. `<REPO_ID>`, `<TASK_ID>`, `<DISPATCH_ID>`,
`<BRANCH>`, and `<GATE_ID>` are printed by the command that precedes them.

> Run these from an Orca agent chat or Orca-managed terminal so Orca can bind the
> Run to your coordinator. If you run from an external shell, pass
> `--from <terminal-handle>` (see `orca terminal list --json`) or drive the same
> steps from the Orca UI.

---

## 0. Setup (once, before the audience arrives)

```bash
orca status --json                     # runtime is up
orca repo add --path "$PWD" --json     # skip if already registered
orca repo list --json                  # find "orca-demo", copy its id
orca repo set-base-ref --repo id:<REPO_ID> --ref main
make test                              # baseline is green: 20 tests
```

If `orca` reports `runtime_access_denied`, you are in a sandboxed shell: run the
same command from an Orca terminal, or re-run it with your sandbox's escalation.

Give the audience a baseline to compare against:

```bash
git tag demo-baseline
make report
orca worktree ps
```

---

## 1. The baseline (1 min)

Say: *"20 events, 4 errors, 982 seconds. One text renderer. This is the app the
team has today."*

```bash
make test
make report
```

Point at the repo map: `pulse/` (4 small modules), `tests/`, `tasks/` (the specs
we are about to hand out).

---

## 2. Fan out: three workers, three worktrees (3 min)

Create the Run (optional — the first `worker-start` would do it):

```bash
orca orchestration run-create \
  --objective "Pulse 0.2: filters + markdown + html renderers"
```

Start all three. Note the different agents: the point is that the spec is the
interface, not the model.

```bash
orca orchestration worker-start \
  --spec-file tasks/01-filters.md \
  --task-title "Filters: window/level/service" \
  --worktree new-top-level --repo id:<REPO_ID> --name filters \
  --agent codex

orca orchestration worker-start \
  --spec-file tasks/02-markdown.md \
  --task-title "Renderer: markdown" \
  --worktree new-top-level --repo id:<REPO_ID> --name markdown \
  --agent claude

orca orchestration worker-start \
  --spec-file tasks/03-html.md \
  --task-title "Renderer: html" \
  --worktree new-top-level --repo id:<REPO_ID> --name html \
  --agent codex
```

**Then stop talking and end your turn.** Orca wakes you when each worker reports.
Bonus talking point while they work: `orca worktree ps` and
`orca worktree list` show three live checkouts; each receipt named its branch.

Show the isolation in git:

```bash
git log --oneline --graph --all --decorate
```

Say: *"Three branches, zero shared files. The merge is boring by construction."*

---

## 3. Steer one worker (1 min)

While a worker is still running, send it a message. It receives it when its
current turn ends; the worker does not need to be restarted.

```bash
orca orchestration send \
  --to dispatch:<DISPATCH_ID> \
  --subject "Contract reminder" \
  --body "Keep the public API exactly as specced. Do not edit pulse/cli.py."
```

If a worker asks a question, answer it (in a chat Orca delivers it; from a shell
use `reply`):

```bash
orca orchestration reply --id <MESSAGE_ID> --body "<answer>"
```

Inspect a worker without stealing its terminal:

```bash
orca orchestration worker-show --dispatch <DISPATCH_ID>
orca orchestration worker-read --dispatch <DISPATCH_ID> --limit 20
```

---

## 4. Fan in: merge, gate, integrate (3 min)

Each `worker_done` gives you a task id and branch. Merge the three:

```bash
git switch main
git merge --no-ff <FILTERS_BRANCH>  -m "feat: filters (codex worker)"
git merge --no-ff <MARKDOWN_BRANCH> -m "feat: markdown renderer (claude worker)"
git merge --no-ff <HTML_BRANCH>     -m "feat: html renderer (codex worker)"
make test                            # baseline suite + every worker's new tests
```

Now show a **decision gate**. Create the dependent Task explicitly, then block it.
`--deps` takes the three worker task ids from the `worker_done` receipts:

```bash
orca orchestration task-create \
  --spec-file tasks/04-integration.md \
  --task-title "CLI integration" \
  --deps '["<FILTERS_TASK>","<MARKDOWN_TASK>","<HTML_TASK>"]'
# -> prints <INTEGRATION_TASK_ID>

orca orchestration gate-create \
  --task <INTEGRATION_TASK_ID> \
  --question "Merge complete and tests green — start integration?" \
  --options '["start","hold"]'
# -> prints <GATE_ID>

orca orchestration gate-list
orca orchestration gate-resolve --id <GATE_ID> --resolution "start"
```

Start the integration worker **from that gated Task** (not a new spec, so the
gate and dependencies still apply), branched from the merged `main`:

```bash
orca orchestration worker-start \
  --task <INTEGRATION_TASK_ID> \
  --worktree new-top-level --repo id:<REPO_ID> --name integrate \
  --base-branch main --agent codex
```

Say: *"This is the DAG: three parallel leaves, one join that owns the only shared
file."*

---

## 5. Cross-agent review (2 min)

Merge the integration branch, then have a **different agent** review the result:

```bash
git switch main
git merge --no-ff <INTEGRATION_BRANCH> -m "feat: wire filters and renderers into CLI"

orca orchestration worker-start \
  --spec-file tasks/05-review.md \
  --task-title "Review: contracts, escaping, tests" \
  --worktree new-top-level --repo id:<REPO_ID> --name review \
  --agent claude
```

The reviewer writes `docs/review-notes.md` — findings with `file:line`, no code
changes. Merge it and show it:

```bash
git merge --no-ff <REVIEW_BRANCH> -m "docs: review notes"
cat docs/review-notes.md
```

---

## 6. The payoff (1 min)

```bash
make test
python3 -m pulse report data/sample_events.jsonl --format text
python3 -m pulse report data/sample_events.jsonl --format markdown
python3 -m pulse report data/sample_events.jsonl --format html
python3 -m pulse report data/sample_events.jsonl --window 5m --level error
```

Then the one slide that says it all:

```bash
git log --graph --oneline --decorate --all
orca worktree ps
```

Say: *"Five agents, five branches, one coordinator, and every claim is backed by
a test run. That's the orchestration."*

---

## Reset between demos

```bash
orca worktree list                     # remove what you created
orca worktree rm --worktree name:filters    --delete-branch
orca worktree rm --worktree name:markdown   --delete-branch
orca worktree rm --worktree name:html       --delete-branch
orca worktree rm --worktree name:integrate  --delete-branch
orca worktree rm --worktree name:review     --delete-branch

git switch main
git reset --hard demo-baseline         # destructive: back to the tagged baseline
git clean -fd
```

`git reset --hard` is only safe here because `demo-baseline` is the tagged,
committed starting point. Do not run it in a repo with work you care about.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `runtime_access_denied` | The shell is sandboxed. Run from an Orca terminal, or re-run with escalation. Never run `orca open` to fix this. |
| `worker-start` exits non-zero | Read `failedStage` in the JSON; do not re-run blindly. Check `orca worktree list` for a half-created worktree. |
| Worker never reports | You are polling. End your turn; Orca wakes you on `worker_done`, `question`, or `escalation`. |
| Merge conflict | A worker edited outside its owned files. Send it back rather than fixing by hand — that is the demo's lesson. |
| Branch name unknown | `git -C <worktree-path> branch --show-current`, or read the `worker-start` receipt. |
| New worktree kept open | Expected: `new-top-level` workers stay open so you can talk to them. Release with `orca orchestration worker-release --dispatch <ID>`. |

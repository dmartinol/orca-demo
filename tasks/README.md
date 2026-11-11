# Task specs

One coordinator brief, two worker specs, one handoff artifact: the pull request.

| Spec | Who runs it | Works in | Produces |
| --- | --- | --- | --- |
| `00-run-demo.md` | the coordinator (any Orca agent) | its own chat — never the checkout | the final report: PR URL + review verdict |
| `01-implement-issue.md` | implementer (codex · gpt-5.6-luna high) | new worktree, new branch | commit + pushed branch + PR |
| `02-review-pr.md` | reviewer (opencode · gpt-6-luna xhigh) | the implementer's worktree | a review on the PR |

The coordinator wires them with `--deps`: the reviewer task is created blocked
on the implementer task and is started only when it completes. Worker specs are
self-contained — the reviewer finds its PR from the checkout — so the only
thing that changes per run is the issue number:

```bash
--spec "Read tasks/01-implement-issue.md and implement issue #1. Open a PR when green."
```

The spec file holds the durable part — constraints, checklist, evidence — while
the one-line dispatch carries the number that changes per run.

# Task specs

Two specs, two workers, one handoff artifact: the pull request.

| Spec | Worker | Works in | Produces |
| --- | --- | --- | --- |
| `01-implement-issue.md` | implementer (codex --profile enmaas) | new worktree, new branch | commit + pushed branch + PR |
| `02-review-pr.md` | reviewer (opencode --standalone) | the implementer's worktree | a review on the PR |

The dispatch prompt names the issue or PR number and points at the spec, e.g.

```bash
--spec "Read tasks/01-implement-issue.md and implement issue #1. Open a PR when green."
```

The spec file holds the durable part — constraints, checklist, evidence — while
the one-line dispatch carries the number that changes per run.

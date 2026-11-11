# Task 05 — Cross-agent review

You are an independent reviewer. The feature and integration work is complete; do
not change code. Your job is to produce a short, evidence-based review that a
human can act on.

## Goal

Create `docs/review-notes.md`.

## Files you own

Create only `docs/review-notes.md`. Do not edit source, tests, `README.md`,
`Makefile`, or anything else.

## What to review

1. Read `pulse/*.py`, `tests/*.py`, and `tasks/01-filters.md` through
   `tasks/04-integration.md`.
2. Run `make test` and the three demo commands from `tasks/04-integration.md`.
3. Inspect the diff on your base branch if one is available
   (`git log --oneline -10`, `git diff <base>...HEAD --stat`).

## Review checklist

- **Contract drift** — does each module match the signatures and semantics in its
  task spec? Especially `filter_events` (`None` vs empty list), `parse_window`
  errors, and the `summary` keys every renderer expects.
- **Injection / escaping** — HTML escaping of service names and levels,
  Markdown table escaping, no raw user text in HTML.
- **Error handling** — bad window, unreadable file, malformed line: friendly
  stderr and exit code 2, never a traceback.
- **Correctness edge cases** — empty log, single event, naive timestamps,
  timezone offsets, duplicate flags.
- **Tests** — are the important behaviours actually asserted, or only smoke
  tested?
- **CLI UX** — help text, default format, filter interaction.

## Required format for `docs/review-notes.md`

```markdown
# Pulse review notes

Reviewed at <commit> on <date>.

## Summary
- <three bullets at most>

## Findings

| Severity | Location | Finding | Suggested fix |
| --- | --- | --- | --- |
| high/medium/low | `path:line` | ... | ... |

## Test evidence
<paste the final line of `make test` and the commands you ran>
```

Rules: every finding must cite `file:line`; no finding without evidence; if you
find nothing at a severity, say so explicitly. Do not rewrite the code in the
document.

## Definition of done

`docs/review-notes.md` exists, follows the format, and the test evidence section
reflects a real run.

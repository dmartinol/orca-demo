# Review a pull request

Your task names an **issue number**: review the open PR that closes it. You are
reviewing, not implementing: the checkout is already on the PR branch.

## Steps

1. Find the PR and read it. The checkout is on the PR branch, so `gh pr view`
   with no argument resolves it:

   ```bash
   gh pr view --json number,title,body,files,commits,headRefName,baseRefName
   gh pr diff
   ```

   If that finds nothing, locate it by the issue it closes and check it out:

   ```bash
   gh pr list --state open --search "Closes #<N>" --json number,title,headRefName
   gh pr checkout <PR>
   ```

2. Read the linked issue and check the implementation against **its acceptance
   criteria**, not against your own taste.
3. Run the suite: `make test`. Run the feature command if the issue names one.
4. Review the diff for:
   - acceptance criteria actually met (cite `file:line`);
   - the `summarize()` contract respected, existing behaviour unchanged;
   - escaping of untrusted log values (Markdown/HTML injection);
   - empty-input and boundary cases;
   - tests that assert behaviour, not just import the module;
   - unrelated changes or scope creep.
5. Post **one** review on the PR:

   ```bash
   gh pr review <PR> --comment --body-file /tmp/review.md
   # or, when it is clean:
   gh pr review <PR> --approve --body-file /tmp/review.md
   # or, for real blockers only:
   gh pr review <PR> --request-changes --body-file /tmp/review.md
   ```

## Review body format

```markdown
## Verdict
approve / comment / request changes — one sentence why.

## Acceptance criteria
- [x] criterion — `file:line`
- [ ] criterion — what is missing

## Findings
| Severity | Location | Finding | Suggestion |
| --- | --- | --- | --- |
| high/medium/low | `path:line` | ... | ... |

## Test evidence
<the command you ran and its final line>
```

Every finding needs a `file:line`. If you find nothing at a severity, say so.

## Constraints

- **Read-only**: do not edit files, commit, push, merge, or close the PR.
- Do not approve a PR with failing tests or an unmet acceptance criterion.
- Do not restyle or rewrite the implementation in the review; describe the fix.

## Definition of done

Report back with: PR URL, the review state you posted (approved / commented /
changes requested), and your top findings. A `worker_done` without a posted
review is not done.

# Implement a GitHub issue

Your task names an **issue number**. Read it first:

```bash
gh issue view <N> --json number,title,body,labels
```

**The issue body is the spec.** Its acceptance criteria and constraints are
binding; this file only adds the workflow and the definition of done.

## Steps

1. Read the issue, `README.md`, and the relevant modules under `pulse/`.
2. Implement the feature in this checkout. Match the existing style; Python
   3.11, standard library only.
3. Add or extend tests under `tests/`. Run `make test` until it is green.
4. Commit with a focused conventional message
   (e.g. `feat: add markdown report format`).
5. Push the branch: `git push -u origin HEAD`.
6. Open a pull request against `main`:

   ```bash
   gh pr create \
     --title "<issue title>" \
     --body "Closes #<N>

   ## What changed
   - ...

   ## Verification
   \`make test\` → <final result line>
   \`python3 -m pulse report data/sample_events.jsonl --format markdown\` → ok"
   ```

## Constraints

- Do **not** push to `main`, force-push, merge, or close the issue.
- Do **not** edit files outside the issue's scope. If the issue is silent, keep
  the diff minimal and say what you touched in the PR body.
- Do **not** add dependencies.
- If the issue is ambiguous or blocked, ask the coordinator instead of guessing.

## Definition of done

Report back with: branch name, commit sha, PR URL, the exact test command you
ran, and its final result line. A `worker_done` without a PR URL is not done.

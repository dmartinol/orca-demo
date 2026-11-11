# Task specs

Each file in this folder is a **self-contained prompt** for one orchestration worker.
The coordinator passes a spec to Orca verbatim:

```bash
orca orchestration worker-start --spec-file tasks/01-filters.md ...
```

Why they are files instead of chat messages:

- The spec is reviewable, versionable, and reusable across demo runs.
- It names the files the worker may edit, so parallel workers stay in disjoint
  file sets and merge without conflicts.
- It states the evidence required (`make test` green, command output) so a
  `worker_done` is verifiable instead of "trust me".

| Spec | Worker owns | Depends on |
| --- | --- | --- |
| `01-filters.md` | `pulse/filters.py`, `tests/test_filters.py` | — |
| `02-markdown.md` | `pulse/render_markdown.py`, `tests/test_render_markdown.py` | — |
| `03-html.md` | `pulse/render_html.py`, `tests/test_render_html.py` | — |
| `04-integration.md` | `pulse/cli.py`, `tests/test_cli_formats.py` | 01, 02, 03 |
| `05-review.md` | `docs/review-notes.md` | 04 |

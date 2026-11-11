# Agent instructions

Pulse is a tiny incident-report CLI: JSON-lines event logs in, a summarized
report out. Python 3.11, standard library only. The human-facing overview and
the Orca orchestration demo live in `README.md`; this file tells a coding agent
how to work in the repo.

## Commands

- **Test:** `make test` — `unittest` over `tests/`, 20 tests, runs in
  milliseconds. Must be green before you report done.
- **Run:** `make report`, or `python3 -m pulse report data/sample_events.jsonl
  [--format text]`.
- **Clean:** `make clean` (removes `__pycache__/` and `out/`).

## Code style

- Python 3.11, standard library only. Never add a dependency.
- Match the existing modules: one small module per concern, a top docstring,
  type hints where the code already uses them.
- Commit messages are focused and conventional, e.g. `feat: add markdown
  report format`.

## Architecture

- `pulse/loader.py` parses and validates events; parse failures raise
  `EventError`.
- `pulse/summarize.py` — `summarize()` returns one documented dict. This is the
  **stable contract**; renderers are written against it.
- `pulse/render.py` holds the renderers; they are registered in the `FORMATS`
  table in `pulse/cli.py`. Add an output format by adding a renderer and one
  registry entry — `loader` and `summarize` stay untouched.
- `tests/` mirrors the modules; test behavior, not snapshots of the sample file.

Demo material, not product code: `tasks/` (worker specs), `docs/` (runbook,
orchestration vocabulary), and `opencode.json` (pins the reviewer demo's model).

## Traps

- **Event logs are untrusted input.** Any renderer must escape values before
  emitting them; escaping is an explicit review item for every new format.
- **No wall-clock time.** Time windows are computed from the last event in the
  file so output is deterministic. Never use `datetime.now()` or similar.
- **`data/sample_events.jsonl` is canned demo input.** Do not regenerate or edit
  it; new fixtures go under `tests/`.
- **Never push to `main`**, force-push, or merge. Work on a branch and open a
  PR; the PR is the handoff artifact.
- **Generated files are never committed**: `__pycache__/`, `out/`.

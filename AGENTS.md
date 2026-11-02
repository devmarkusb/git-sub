# Agent Instructions

## Project overview

`git-sub` is a Python 3.8+ command-line script that initializes recursive Git submodules and, when tracked files use Git
LFS, configures local LFS and pulls its content. The executable is the extensionless `git-sub` file.

## Build commands

- No package build command is defined or used by CI.
- Development setup: `python3 -m venv .venv`; activate with `source .venv/bin/activate` (Windows:
  `.venv\Scripts\activate`), then run `pip install -e ".[dev]"`.
- README hook setup: `git config core.hooksPath .githooks`.

## Test commands

- CI test command: `pytest -q tests/`.
- `pytest` is also documented for local development.

## Formatting and linting

- Markdown check: `python tools/format_markdown.py --check --tracked`.
- Ruff: `ruff check git-sub tests tools/format_markdown.py`.
- The pre-commit hook formats staged Markdown and re-stages formatter changes. It refuses partially staged Markdown.

## Architecture and important directories

- `git-sub`: CLI implementation; subprocess calls invoke Git and Git LFS.
- `tests/`: pytest unit tests; subprocess interactions are mocked.
- `tools/format_markdown.py`: Markdown formatter used by CI and `.githooks/pre-commit`.
- `.github/workflows/ci.yml`: CI matrix for Ubuntu, macOS, and Windows with Python 3.8 and 3.12.

## Coding conventions

- Keep runtime compatibility with Python 3.8 and Ruff's `py38` target.
- Follow the configured Ruff rules (`E`, `F`, `I`, `UP`, `B`) and 120-character line length.
- Keep `git-sub` executable and preserve its standalone, dependency-free runtime behavior.

## Testing expectations

- For behavior changes, add focused tests in `tests/` and mock subprocess calls; do not use a real repository.
- Keep the CI commands above aligned with changes to project tooling.

## Files and directories agents must not edit without explicit approval

- Ask before changing secrets, local environment files, generated code, deployment configuration, migrations, vendored
  code, lockfiles, or release workflows.
- Do not stage generated output: `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, or `*.egg-info/`.
- Do not change `.github/workflows/` or dependency/build metadata in `pyproject.toml` unless the task calls for it.

## Security and privacy constraints

- Running `git-sub` changes the current checkout: it updates recursive submodules and can download Git LFS content.
  Run it only when requested and in the intended repository.
- Do not add automatic Git LFS installation, privilege escalation, or shell-based subprocess execution. The tool must
  continue to rely on Git and Git LFS already available on `PATH`.
- Never push, force-push, or use an equivalent publishing flow (including `gh` or IDE sync) without explicit user
  approval.

## Review checklist before final response

- Keep changes scoped to this repository; it may be embedded as a submodule in another checkout.
- Review `git status` and the final diff from this repository, and ensure no generated files are included.
- Report which documented checks were run; do not claim checks passed if they were not run.

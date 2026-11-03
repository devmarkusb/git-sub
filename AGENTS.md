# Agent Instructions

## Project overview

`git-sub` is a Python 3.8+ command-line script that syncs registered submodule URLs from `.gitmodules`, initializes
recursive Git submodules and, when tracked files use Git LFS, configures local LFS and pulls its content. The executable
is the extensionless `git-sub` file.

## Build commands

- No package build command is defined or used by CI.
- Development tooling requires Python 3.10+; the `git-sub` runtime remains Python 3.8+.
- Development setup: `python3 -m venv .venv`; activate with `source .venv/bin/activate` (Windows:
  `.venv\Scripts\activate`), then run `pip install -e ".[dev]"`.
- Hook setup: `pre-commit install`. For an existing `.githooks` setup, first remove its local override with
  `git config --local --unset-all core.hooksPath`.

## Test commands

- Full development test command: `pytest -q tests/`.
- Python 3.8 runtime-only setup: `pip install -e ".[test]"`, then `pytest -q tests/test_gitsub.py`.
- CI runs runtime tests on Python 3.8 and 3.12; tooling checks run on 3.12.

## Formatting and linting

- Markdown formatting/check: `pre-commit run mdformat --all-files --show-diff-on-failure`.
- Markdown policy is in `.mdformat.toml`; formatter versions are pinned in `.pre-commit-config.yaml`.
- Ruff: `ruff check git-sub tests`.
- The standard pre-commit hook automatically formats staged Markdown and temporarily saves unstaged changes. When it
  edits files, review and stage the result, then retry the commit.

## Architecture and important directories

- `git-sub`: CLI implementation; subprocess calls invoke Git and Git LFS.
- `tests/`: pytest unit tests; subprocess interactions are mocked.
- `.pre-commit-config.yaml`: official mdformat hook with GFM support; pre-commit manages file selection and hook
  environments. Keep Markdown parsing and hook execution in the upstream tools.
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

- Running `git-sub` changes the current checkout: it resets registered submodule URL overrides to `.gitmodules`, updates
  recursive submodules, and can download Git LFS content. Run it only when requested and in the intended repository.
- Do not add automatic Git LFS installation, privilege escalation, or shell-based subprocess execution. The tool must
  continue to rely on Git and Git LFS already available on `PATH`.
- Never push, force-push, or use an equivalent publishing flow (including `gh` or IDE sync) without explicit user
  approval.

## Review checklist before final response

- Keep changes scoped to this repository; it may be embedded as a submodule in another checkout.
- Review `git status` and the final diff from this repository, and ensure no generated files are included.
- Report which documented checks were run; do not claim checks passed if they were not run.

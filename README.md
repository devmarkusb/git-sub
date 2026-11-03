# git-sub

[![CI](https://github.com/devmarkusb/git-sub/actions/workflows/ci.yml/badge.svg)](https://github.com/devmarkusb/git-sub/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Submodule init + Git LFS pull in one step** — plain Python 3. Same `git` and `git-lfs` you already use on **macOS,
Linux, and Windows** (Git for Windows).

## What it does

1. `git submodule sync --recursive` to align registered submodule URLs with `.gitmodules`.
2. `git submodule update --init --recursive` (uses `--recommend-shallow` when your Git supports it).
3. If the repo uses **Git LFS** (`filter=lfs` in tracked `.gitattributes`), runs `git lfs install --local` and
   `git lfs pull`.

LFS setup and pull apply to the invoked repository; `git-sub` does not run them separately inside submodules.

URL sync makes `.gitmodules` authoritative and resets per-checkout submodule URL overrides. It runs again after a
successful update to pick up newly checked-out nested `.gitmodules` files. If a nested URL change causes the update
itself to fail, another invocation may be needed; failed updates are not automatically retried.

It does **not** install `git-lfs` for you (no `sudo` / Homebrew automation). Install LFS once per machine; see
[git-lfs.com](https://git-lfs.com).

## Usage

Run inside any clone or worktree (usually your current directory):

```text
git-sub
git-sub --help
```

Commands operate on that repository's root, including when invoked from a subdirectory.

## Companion: [git-worktree](https://github.com/devmarkusb/git-worktree)

> **Separate project.** The section below is only for people who also use
> **[git-worktree](https://github.com/devmarkusb/git-worktree)** (worktree add/remove + optional `git-sub`). You can
> ignore it if you only run `git-sub` by hand.

That companion tool looks for a richer `git-sub` in this order:

1. **`GIT_SUB`** — absolute path to this `git-sub` file (or any executable you prefer).

2. **`git-sub` on your PATH** — e.g. both scripts copied or linked into `~/bin`.

3. **Sibling checkout** — clone this repo next to `git-worktree` so you have:

   - `…/git-worktree/git-worktree`
   - `…/git-sub/git-sub`

   Same parent folder, fixed names — **no extra config**.

4. If none of the above match, `git-worktree` falls back to a minimal built-in submodule-only step.

Low-friction layout if you use both:

```text
~/src/git-worktree/   # https://github.com/devmarkusb/git-worktree
~/src/git-sub/        # this repo
```

Run `git-worktree` from the first checkout (or symlink it onto your `PATH`). No pip, no global install required.

## Requirements

- Python 3.8+
- `git` on PATH
- `git-lfs` on PATH **only** when the repository actually uses LFS

## Development

Development tooling requires Python 3.10+; running the standalone `git-sub` script still requires only Python 3.8+.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
pre-commit run mdformat --all-files
ruff check git-sub tests
pytest
```

If you previously enabled `.githooks`, run `git config --local --unset-all core.hooksPath` before `pre-commit install`.

The standard pre-commit hook automatically formats staged Markdown with mdformat and GitHub Flavored Markdown support.
It uses 120-column prose wrapping and the policy in `.mdformat.toml`; formatter versions are pinned in
`.pre-commit-config.yaml`. Pre-commit manages its own formatter environment and temporarily saves unstaged changes while
running. When formatting changes a file, the commit pauses: review and stage the formatted result, then retry the
commit. To format a specific file, run `pre-commit run mdformat --files README.md`.

CI runs runtime tests on Ubuntu, macOS, and Windows with Python 3.8 and 3.12. The Markdown hook and Ruff run on Python
3.12. For runtime-only testing with Python 3.8, install `pip install -e ".[test]"` and run
`pytest -q tests/test_gitsub.py`.

## License

MIT — see [LICENSE](LICENSE).

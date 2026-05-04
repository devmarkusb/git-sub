# git-sub

**Submodule init + Git LFS pull in one step** — plain Python 3, no Bash. Same `git` and `git-lfs` you already use on **macOS, Linux, and Windows** (Git for Windows).

## What it does

1. `git submodule update --init --recursive` (uses `--recommend-shallow` when your Git supports it).
2. If the repo uses **Git LFS** (`filter=lfs` in tracked `.gitattributes`), runs `git lfs install --local` and `git lfs pull`.

It does **not** install `git-lfs` for you (no `sudo` / Homebrew automation). Install LFS once per machine; see [git-lfs.com](https://git-lfs.com).

## Usage

Run inside any clone or worktree (usually your current directory):

```text
git-sub
git-sub --help
```

## Use with git-worktree

That tool looks for a richer `git-sub` in this order:

1. **`GIT_SUB`** — absolute path to this `git-sub` file (or any executable you prefer).
2. **`git-sub` on your PATH** — e.g. both scripts copied into `~/bin`.
3. **Sibling checkout** — clone this repo next to `git-worktree` so you have:
   - `…/git-worktree/git-worktree`
   - `…/git-sub/git-sub`  
   Same parent folder, fixed names — **no extra config**.
4. If none of the above match, `git-worktree` falls back to a minimal built-in submodule-only step.

So the low-friction layout is:

```text
~/src/git-worktree/   # clone of git-worktree repo
~/src/git-sub/        # clone of git-sub repo
```

Keep using `~/src/git-worktree/git-worktree` (or add that directory to PATH and run the script by name). No pip, no global install required.

## Requirements

- Python 3.8+
- `git` on PATH
- `git-lfs` on PATH **only** when the repository actually uses LFS

## License

MIT — see [LICENSE](LICENSE).

#!/usr/bin/env python3
"""Wrap Markdown prose to a fixed width and optionally apply it to staged files."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import textwrap
from pathlib import Path

DEFAULT_WIDTH = 120

FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
LIST_RE = re.compile(r"^(\s*)((?:[-+*]|\d+[.)])\s+)(.*)$")
BLOCKQUOTE_RE = re.compile(r"^(>\s?)(.*)$")


def is_special_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith(("#", "|", "<", "[![")):
        return True
    if stripped.startswith(("```", "~~~")):
        return True
    if stripped in ("---", "***", "___"):
        return True
    if line.startswith(" "):
        return True
    if line.startswith(("    ", "\t")):
        return True
    if re.match(r"^\s*\|?.+\|.+\|?\s*$", line):
        return True
    if re.match(r"^\s*\[[^\]]+\]:\s+", line):
        return True
    return False


def wrap_words(text: str, *, width: int, initial: str = "", subsequent: str = "") -> list[str]:
    if not text:
        return [initial.rstrip()]
    return textwrap.wrap(
        text,
        width=width,
        initial_indent=initial,
        subsequent_indent=subsequent,
        break_long_words=False,
        break_on_hyphens=False,
    )


def wrap_paragraph(lines: list[str], *, width: int) -> list[str]:
    text = " ".join(line.strip() for line in lines)
    return wrap_words(text, width=width)


def wrap_prefixed_line(line: str, *, width: int) -> list[str] | None:
    list_match = LIST_RE.match(line)
    if list_match:
        indent, marker, text = list_match.groups()
        return wrap_words(
            text.strip(),
            width=width,
            initial=f"{indent}{marker}",
            subsequent=" " * (len(indent) + len(marker)),
        )

    quote_match = BLOCKQUOTE_RE.match(line)
    if quote_match:
        marker, text = quote_match.groups()
        return wrap_words(text.strip(), width=width, initial=marker, subsequent=marker)

    return None


def format_text(text: str, *, width: int = DEFAULT_WIDTH) -> str:
    lines = text.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    in_fence = False

    def flush_paragraph() -> None:
        if paragraph:
            output.extend(wrap_paragraph(paragraph, width=width))
            paragraph.clear()

    for line in lines:
        if FENCE_RE.match(line):
            flush_paragraph()
            output.append(line.rstrip())
            in_fence = not in_fence
            continue

        if in_fence:
            output.append(line.rstrip())
            continue

        if not line.strip():
            flush_paragraph()
            output.append("")
            continue

        prefixed = wrap_prefixed_line(line, width=width)
        if prefixed is not None:
            flush_paragraph()
            output.extend(prefixed)
            continue

        if is_special_line(line):
            flush_paragraph()
            output.append(line.rstrip())
            continue

        if line.endswith(("  ", "\\")):
            flush_paragraph()
            output.append(line.rstrip())
            continue

        paragraph.append(line)

    flush_paragraph()
    trailing_newline = "\n" if text.endswith("\n") else ""
    return "\n".join(output) + trailing_newline


def format_file(path: Path, *, width: int = DEFAULT_WIDTH) -> bool:
    original = path.read_text(encoding="utf-8")
    formatted = format_text(original, width=width)
    if formatted == original:
        return False
    path.write_text(formatted, encoding="utf-8")
    return True


def git_lines(args: list[str]) -> list[str]:
    result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return [line for line in result.stdout.splitlines() if line]


def staged_markdown_files() -> list[Path]:
    names = git_lines(
        ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "--", "*.md", "*.markdown"]
    )
    return [Path(name) for name in names]


def has_unstaged_changes(path: Path) -> bool:
    result = subprocess.run(["git", "diff", "--quiet", "--", str(path)])
    return result.returncode != 0


def format_staged_files(*, width: int) -> int:
    paths = staged_markdown_files()
    partially_staged = [path for path in paths if has_unstaged_changes(path)]
    if partially_staged:
        print("Refusing to format partially staged Markdown files:", file=sys.stderr)
        for path in partially_staged:
            print(f"  {path}", file=sys.stderr)
        print("Stage or stash unstaged Markdown changes, then commit again.", file=sys.stderr)
        return 1

    changed = [path for path in paths if path.is_file() and format_file(path, width=width)]
    if changed:
        subprocess.run(["git", "add", "--", *(str(path) for path in changed)], check=True)
        print("Formatted Markdown:")
        for path in changed:
            print(f"  {path}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--staged", action="store_true", help="format staged Markdown files")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    if args.staged:
        if args.paths:
            print("--staged cannot be combined with explicit paths", file=sys.stderr)
            return 2
        return format_staged_files(width=args.width)

    if not args.paths:
        print("No Markdown files supplied.", file=sys.stderr)
        return 2

    for path in args.paths:
        format_file(path, width=args.width)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

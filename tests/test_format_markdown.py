from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "tools" / "format_markdown.py"


def load_format_markdown():
    path = str(SCRIPT_PATH)
    loader = SourceFileLoader("format_markdown_under_test", path)
    spec = importlib.util.spec_from_loader(loader.name, loader, origin=path)
    if spec is None:
        raise RuntimeError(f"Could not build spec for {SCRIPT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def test_wraps_plain_markdown_paragraphs():
    fm = load_format_markdown()
    source = "This is a long Markdown paragraph that should be wrapped without changing words.\n"

    assert fm.format_text(source, width=40) == (
        "This is a long Markdown paragraph that\n"
        "should be wrapped without changing\n"
        "words.\n"
    )


def test_wraps_list_items_with_continuation_indent():
    fm = load_format_markdown()
    source = "- This list item should wrap onto the next line with the text aligned.\n"

    assert fm.format_text(source, width=34) == (
        "- This list item should wrap onto\n"
        "  the next line with the text\n"
        "  aligned.\n"
    )


def test_preserves_markdown_structural_lines():
    fm = load_format_markdown()
    source = (
        "# Heading With A Long Name That Should Stay On One Line\n"
        "\n"
        "| Column | Value |\n"
        "| --- | --- |\n"
        "| a | b |\n"
        "\n"
        "```text\n"
        "this line is deliberately left untouched by the formatter\n"
        "```\n"
        "\n"
        "[![CI](https://example.invalid/a/really/long/badge/url.svg)](https://example.invalid)\n"
    )

    assert fm.format_text(source, width=30) == source


def test_preserves_indented_list_continuation_lines():
    fm = load_format_markdown()
    source = (
        "1. Parent item:\n"
        "   - nested item\n"
        "   Then run this command from the checkout.\n"
    )

    assert fm.format_text(source, width=30) == source

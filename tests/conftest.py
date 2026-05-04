from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "git-sub"


@pytest.fixture(scope="module")
def gitsub():
    # Extensionless script: spec_from_file_location can return None; use SourceFileLoader.
    loader = importlib.machinery.SourceFileLoader("gitsub", str(SCRIPT))
    spec = importlib.util.spec_from_loader("gitsub", loader)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

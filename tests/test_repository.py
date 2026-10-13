from __future__ import annotations

from pathlib import Path


def test_repository_has_required_files() -> None:
    required = [
        Path("README.md"),
        Path("requirements.txt"),
        Path(".env.example"),
        Path("ramy/config.py"),
        Path("ramy/strategy.py"),
        Path("ramy/risk.py"),
        Path("tests/test_smoke.py"),
    ]
    for path in required:
        assert path.exists(), f"missing required file: {path}"

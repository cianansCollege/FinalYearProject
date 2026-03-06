"""Shared path configuration for Prototype2 scripts.

Environment overrides:
- FYP_DATA_DIR: root directory for data files
- FYP_METADATA_DIR: root directory for metadata CSV files
"""

from __future__ import annotations

import os
from pathlib import Path


PROTOTYPE2_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = PROTOTYPE2_DIR.parent


def _resolve_env_path(env_name: str, default: Path) -> Path:
    value = os.environ.get(env_name)
    if value:
        return Path(value).expanduser().resolve(strict=False)
    return default.resolve(strict=False)


def _first_existing(candidates: list[Path], fallback: Path) -> Path:
    for path in candidates:
        if path.exists():
            return path
    return fallback


DEFAULT_DATA_DIR = _first_existing(
    [REPO_DIR / "Data", PROTOTYPE2_DIR / "Data"],
    REPO_DIR / "Data",
)
DEFAULT_METADATA_DIR = _first_existing(
    [REPO_DIR / "Metadata", PROTOTYPE2_DIR / "Metadata"],
    PROTOTYPE2_DIR / "Metadata",
)

DATA_DIR = _resolve_env_path("FYP_DATA_DIR", DEFAULT_DATA_DIR)
METADATA_DIR = _resolve_env_path("FYP_METADATA_DIR", DEFAULT_METADATA_DIR)


def prototype2_path(*parts: str) -> Path:
    return PROTOTYPE2_DIR.joinpath(*parts)


def data_path(*parts: str) -> Path:
    return DATA_DIR.joinpath(*parts)


def metadata_path(*parts: str) -> Path:
    return METADATA_DIR.joinpath(*parts)

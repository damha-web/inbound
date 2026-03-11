"""Lightweight .env loader (no external dependency)."""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(env_path: str | Path = ".env", override: bool = False) -> bool:
    path = Path(env_path)
    if not path.exists():
        return False

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        if override or key not in os.environ:
            os.environ[key] = value
    return True

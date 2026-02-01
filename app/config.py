"""App configuration (env-driven).

Keep this module dependency-free; it is imported very early.
"""

from __future__ import annotations

import os
from pathlib import Path


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and v != "" else default


# Where to store local DB/state (relative paths are resolved from cwd).
DATA_DIR = Path(_env("JARVIS_DATA_DIR", ".")).expanduser().resolve()

SQLITE_PATH = Path(_env("JARVIS_SQLITE_PATH", str(DATA_DIR / "jarvis.sqlite3"))).expanduser().resolve()

# Legacy JSON paths (used for import/compat and as a fallback)
INFERENCES_JSON_PATH = Path(_env("JARVIS_INFERENCES_JSON", str(DATA_DIR / "inferences.json"))).expanduser().resolve()
RAW_DATA_JSON_PATH = Path(_env("JARVIS_RAW_DATA_JSON", str(DATA_DIR / "raw_data.json"))).expanduser().resolve()

# Server
HOST = _env("JARVIS_HOST", "0.0.0.0")
PORT = int(_env("JARVIS_PORT", "8000"))

# Processing
PROCESS_BATCH_SIZE = int(_env("JARVIS_PROCESS_BATCH_SIZE", "25"))

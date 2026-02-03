"""Security utilities.

This module is intentionally lightweight and local-only.
Its primary use is to prevent accidental export of secrets.

NOTE: This is a heuristic scan. Any positive hit should block export and
require manual sanitization.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List


DEFAULT_SECRET_PATTERNS: List[str] = [
    r"sk-[a-zA-Z0-9]{20,}",  # OpenAI
    r"sk-ant-[a-zA-Z0-9-]{20,}",  # Anthropic
    r"ghp_[a-zA-Z0-9]{36}",  # GitHub classic token
    r"-----BEGIN [A-Z]+ KEY-----",  # Private keys
    r"Bearer [a-zA-Z0-9-_.]{20,}",  # Bearer tokens
    # Generic-ish patterns (high false-positive risk; keep conservative)
    r"password[\"\s:=]+[^\s]{8,}",
    r"api[_-]?key[\"\s:=]+[^\s]{10,}",
    r"secret[\"\s:=]+[^\s]{10,}",
    r"token[\"\s:=]+[^\s]{20,}",
]


@dataclass
class SecretHit:
    pattern: str
    sample: str


def find_secrets(text: str, patterns: Iterable[str] = DEFAULT_SECRET_PATTERNS) -> List[SecretHit]:
    hits: List[SecretHit] = []
    for pat in patterns:
        try:
            matches = re.findall(pat, text, flags=re.IGNORECASE)
        except re.error:
            continue
        if not matches:
            continue
        for m in matches:
            s = m if isinstance(m, str) else str(m)
            # Don't leak full secret; keep a short prefix only.
            sample = (s[:10] + "...") if len(s) > 10 else (s + "...")
            hits.append(SecretHit(pattern=pat, sample=sample))
    return hits


def safe_to_export(text: str) -> tuple[bool, List[SecretHit]]:
    hits = find_secrets(text)
    return (len(hits) == 0, hits)

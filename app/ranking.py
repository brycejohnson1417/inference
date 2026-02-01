"""Ranking heuristics for triage.

Brenner-ish objective (adapted):
  score ≈ (expected discriminability × option value) / (cost × ambiguity)

We don't have explicit expected information gain estimates yet, so this is a
simple approximation to improve triage order.

Notes:
- Works on the current API fields (id/source/content/inference/confidence).
- If richer schema is present (source_ids, type), we can use it.
"""

from __future__ import annotations

from typing import Any, Dict, List


def triage_score(inf: Dict[str, Any]) -> float:
    conf = float(inf.get("confidence", 0.0) or 0.0)

    # Multi-source bonus if available
    src_ids = inf.get("source_ids")
    multi_bonus = 1.0
    if isinstance(src_ids, list) and len(src_ids) >= 2:
        multi_bonus = 1.15

    # Ambiguity proxy: longer text tends to pack multiple claims.
    text = (inf.get("inference") or inf.get("statement") or "")
    length = max(len(text), 1)
    length_penalty = 1.0
    if length > 220:
        length_penalty = 0.80
    elif length > 140:
        length_penalty = 0.90

    # Source bonus (rough)
    source = (inf.get("source") or "").lower()
    source_bonus = 1.0
    if source in ("chatgpt", "imessage", "safari"):
        source_bonus = 1.05

    return conf * multi_bonus * length_penalty * source_bonus


def sort_inferences(infs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(infs, key=triage_score, reverse=True)

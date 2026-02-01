"""Brenner-style linting for inferences.

Goal: prevent low-quality, non-falsifiable, or self-deceiving inferences from
reaching the triage queue.

This is inspired by BrennerBot's methodology (exclusion tests, third alternative,
chastity vs impotence, anomaly quarantine).

This module is local-only and heuristic by design.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LintIssue:
    code: str
    message: str


def lint_inference_candidate(candidate: Dict[str, Any]) -> List[LintIssue]:
    """Return a list of issues; empty means candidate passes."""
    issues: List[LintIssue] = []

    text = (candidate.get("inference") or candidate.get("statement") or "").strip()
    source = (candidate.get("source") or "").strip().lower()

    if not text:
        issues.append(LintIssue("empty", "Inference text is empty."))
        return issues

    # 1) Trivial / non-actionable
    trivial = [
        "bryce exists",
        "the user exists",
        "this is a message",
        "this is an email",
    ]
    if any(t in text.lower() for t in trivial):
        issues.append(LintIssue("trivial", "Inference appears trivial/non-actionable."))

    # 2) Confidence sanity
    conf = candidate.get("confidence")
    try:
        if conf is not None and not (0.0 <= float(conf) <= 1.0):
            issues.append(LintIssue("confidence_range", "Confidence must be in [0,1]."))
    except Exception:
        issues.append(LintIssue("confidence_parse", "Confidence is not numeric."))

    # 3) Require discriminability hook (Brenner: exclusion / kill test)
    # In MVP, we encode this as requiring either an explicit 'kill_test'
    # or at least one question-like falsifier.
    kill_test = candidate.get("kill_test") or candidate.get("falsifier")
    if not kill_test:
        # soft check: prompt-like strings
        if "never" not in text.lower() and "if" not in text.lower():
            issues.append(
                LintIssue(
                    "no_kill_test",
                    "Missing falsifier/kill-test. Add `kill_test` (e.g., 'If this inference were false, we would observe...').",
                )
            )

    # 4) Third alternative check (Brenner: both could be wrong)
    # If candidate presents an A-vs-B dichotomy, require a third alternative.
    alt = candidate.get("alternatives")
    if (" either " in text.lower() and " or " in text.lower()) and not alt:
        issues.append(
            LintIssue(
                "no_third_alternative",
                "Candidate looks like a dichotomy; add `alternatives` including 'both could be wrong'.",
            )
        )

    # 5) Validity check (chastity vs impotence)
    # For anything derived from a failed action/absence, require distinguishing
    # 'won't' vs 'can't'.
    if any(w in text.lower() for w in ["never", "doesn't", "didn't", "won't", "can't"]):
        if not candidate.get("validity_checks"):
            issues.append(
                LintIssue(
                    "no_validity_check",
                    "Candidate implies an absence/failure; add `validity_checks` to separate measurement failure vs hypothesis failure.",
                )
            )

    return issues


def passes_lint(candidate: Dict[str, Any]) -> bool:
    return len(lint_inference_candidate(candidate)) == 0

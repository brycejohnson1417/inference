# Collaboration Guide

This repository can be reviewed publicly when contributors respect the data boundary: use synthetic inputs, keep generated private outputs out of git, and treat the repo as a prototype for the review workflow.

## Safety Rules

- Do not commit real exports, browser histories, contact records, notes, screenshots, or generated private knowledge files.
- Do not commit `.env` files, API keys, tokens, webhooks, database URLs, or private keys.
- Use `scripts/generate_mock_data.py` for public demos and screenshots.
- Keep JSON outputs ignored unless a specific synthetic fixture is intentionally added.

## Source Of Truth

Use the repo docs and current code as the source of truth before changing behavior.

Recommended read order:

1. `README.md`
2. `docs/PUBLIC_DEMO_BOUNDARY.md`
3. `docs/SYNTHETIC_TRIAGE_FLOW.md`
4. `docs/ARCHITECTURE.md`

## Change Workflow

1. Create a focused branch for a specific improvement.
2. Run the local app with synthetic data.
3. Verify that approved exports still pass the safety gate.
4. Keep screenshots and examples synthetic.
5. Review diffs for accidental private data before committing.

## Review Standard

The most important question is not whether the model can generate claims. The important question is whether the system makes uncertainty visible and prevents unreviewed claims from becoming durable knowledge.

# Public Demo Boundary

This repo can be shown publicly when the demo uses generated mock data and keeps raw personal data out of git, screenshots, and hosted artifacts.

## Safe To Show

- The triage interface with generated mock inferences.
- The synthetic before/after flow in `docs/SYNTHETIC_TRIAGE_FLOW.md`.
- The architecture diagram in `docs/ARCHITECTURE.md`.
- The export safety concept.
- The local-first design boundary.

## Do Not Show Publicly

- Real message exports.
- Real social media exports.
- Real contact data.
- Browser history.
- Raw notes.
- Private screenshots.
- Generated knowledge files based on personal data.
- Any API key, token, private key, database URL, webhook, or deployment secret.

## Demo Setup

```bash
python scripts/generate_mock_data.py
uvicorn app.main:app --reload
```

Open `http://localhost:8000` and use the pending mock inferences.

## Review Principle

Generated claims are untrusted until reviewed. The app is strongest when it shows that boundary clearly: propose, review, approve, export.

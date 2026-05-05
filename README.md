# Inference Triage Program

Inference Triage is a local-first review tool for validating AI-generated claims before they are allowed into a knowledge graph. The core idea is simple: model output should pass through a human approval layer before it becomes durable system memory.

## What It Demonstrates

- Human-in-the-loop validation for AI-generated inferences.
- A swipe-style triage interface for approving, rejecting, and editing claims.
- JSON persistence for approved knowledge graph components.
- Local model experimentation through Ollama.
- Export safety checks that block likely API keys, tokens, and private keys.

## Public Demo Boundary

Use synthetic data for public demos. The included mock-data flow is the safe path for showing the app.

Do not commit real message exports, browser histories, contact exports, social exports, raw notes, private screenshots, or generated knowledge files. The repo's `.gitignore` excludes JSON outputs by default so local generated files are not accidentally published.

## Security Notes

The `/api/export` endpoint performs a heuristic secret scan before exporting approved inferences. If it detects likely credentials, it blocks the export and reports only the count of potential hits.

That scan is a guardrail, not a full data-loss-prevention system. Sensitive data should be kept out of public demos from the start.

## Technical Notes

- FastAPI backend.
- Jinja template and static frontend assets.
- Pydantic models for inference and triage payloads.
- Local JSON persistence for prototype data.
- Optional Ollama model configuration through `OLLAMA_MODEL`.

## Run Locally

Prerequisites: Python 3.10+ and `pip`.

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Optional: choose an Ollama model.
   ```bash
   export OLLAMA_MODEL="llama3.2:3b"
   ```

3. Generate synthetic demo data.
   ```bash
   python scripts/generate_mock_data.py
   ```

4. Start the server.
   ```bash
   uvicorn app.main:app --reload
   ```

5. Open the local app.
   ```text
   http://localhost:8000
   ```

## Current Status

This is a prototype source repo. It is useful for demonstrating the product loop and privacy boundary, but production use would require stronger authentication, encrypted storage, source-level permissions, audit logs, data-retention controls, and more robust export review.

## AI-Assisted Build Note

This prototype was built with AI assistance. The useful work is the system framing: turning uncertain model output into an explicit review queue, identifying privacy failure modes, and adding guardrails before generated knowledge leaves the local environment.

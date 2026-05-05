# Local Inference Triage Guide

This guide describes how to run the prototype locally with generated mock data and evaluate the review workflow without exposing private source material.

## Recommended Local Models

For a laptop-class machine with limited memory, use small or quantized models. The app does not require a hosted model for the public demo path.

Good starting points:

1. **Llama 3.x 8B or smaller**
   - Use a quantized build through Ollama or LM Studio.
   - Useful for lightweight claim generation and summarization tests.

2. **Mistral 7B-class models**
   - Good speed/quality tradeoff for local reasoning tasks.
   - Works well for structured extraction experiments.

Avoid very large or unquantized models on constrained hardware. They will usually run slowly and make the review loop harder to evaluate.

## Local Knowledge Review Loop

The high-level architecture is a local-first review loop:

1. Normalize source material into reviewable snippets.
2. Generate proposed claims from those snippets.
3. Require human approval before claims become durable knowledge.
4. Export only approved structured claims.
5. Block export when likely secrets are detected.

## Safe Demo Path

Use the built-in synthetic data generator:

```bash
python scripts/generate_mock_data.py
uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000
```

## Data Boundary

Public demos should not use real message exports, contact exports, social exports, browser history, notes, screenshots, API keys, tokens, or generated knowledge files based on private data.

The safest public story is the workflow itself: generated claims are useful only after review.

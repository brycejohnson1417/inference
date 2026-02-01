# AI & Digital Spirit Guide

## Recommended Models for MacBook Pro M2 (16GB RAM)

For your hardware (M2 Chip, 16GB RAM), you have a capable machine for local inference, but memory is your main constraint. Running a model *and* your operating system/apps means you should target models that use less than 12GB of RAM comfortably.

**Top Recommendations:**

1.  **Llama 3 (8B Parameters)**
    *   **Why:** State-of-the-art performance for its size.
    *   **Format:** Quantized (Q4_K_M or Q5_K_M).
    *   **Tool:** Use **Ollama** or **LM Studio**.
    *   **Memory:** ~6-8 GB VRAM.

2.  **Mistral 7B (v0.3)**
    *   **Why:** Very capable, efficient, and good at reasoning.
    *   **Format:** Quantized (Q4/Q5).
    *   **Memory:** ~5-7 GB VRAM.

**Avoid:** 70B+ models or unquantized 13B+ models, as they will likely swap to disk and run very slowly on 16GB RAM.

## Architecture: Building Your "Digital Spirit"

To achieve your goal of a cross-silo "Digital Spirit", here is a high-level architecture:

### 1. Data Ingestion (The Silos)
You need scripts to export and normalize data from your sources:
*   **iMessage**: Read local SQLite database (`chat.db` on macOS).
*   **Notes/Email**: Export to text/markdown.
*   **Socials (FB, Insta, X)**: Request GDPR data exports (JSON/HTML).

### 2. The Knowledge Graph (Connecting the Dots)
Instead of just RAG (Vector Search), you want a **Knowledge Graph**.
*   **Nodes**: People, Places, Interests, Events.
*   **Edges**: "Messaged", "Mentioned", "Attended", "Liked".

*Example Inference:*
*   *Input 1 (Text):* "Hey, are we still on for hiking the PCT?" (from `User` to `Bob`).
*   *Input 2 (Insta):* `Bob` follows `#hiking`.
*   *Inference:* `User` and `Bob` share interest `Hiking`.

### 3. Inference Triage (This Program)
This is the "Human-in-the-loop" layer.
*   The AI proposes new edges for the graph (Inferences).
*   **You** validate them (True/False).
*   This creates a "Gold Standard" dataset.

### 4. Fine-Tuning "Ares"
Once you have enough validated inferences:
*   Use them to fine-tune a model (LoRA) or strictly prompt your agent "Ares" on the VPS.
*   Ares uses this structured knowledge to act as your true digital twin.

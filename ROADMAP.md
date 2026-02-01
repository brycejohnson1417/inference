# Digital Alchemy Roadmap: Jarvis to Ares

This document outlines the master plan for your "Digital Self Alchemy" project.

## The Vision
To create a "Digital Spirit" (a distillation of your personality, memories, and preferences) using local hardware, and transfer that spirit into a remote avatar ("Ares").

## Architecture

### 1. The Laboratory: "Jarvis" (Your M2 MacBook Pro)
*   **Role**: The Processor & Gatekeeper.
*   **Why**: Your M2 chip (16GB RAM) is powerful enough to run local embeddings and LLMs (Llama 3, Mistral) privately. We keep the raw data here so it never leaves your control.
*   **Components**:
    *   **Data Silos**: iMessage (`chat.db`), Social Exports, Notes.
    *   **The Brain (Ollama)**: A local LLM that reads raw data and extracts "Inferences" (Facts/Insights).
    *   **The Triage App (This Program)**: You manually review every insight.
        *   *Machine*: "User likes hiking." -> *You*: "True (Approve)".
        *   *Machine*: "User hates pizza." -> *You*: "False (Reject)".
    *   **The Output**: A pure JSON file of *validated* truths. This is the "Digital Spirit".

### 2. The Avatar: "Ares" (VPS / Ubuntu)
*   **Role**: The Active Assistant.
*   **Why**: Running 24/7 on a server to act on your behalf.
*   **Constraint**: 4GB RAM is too small for heavy training, but perfect for *running* a highly optimized agent.
*   **Input**: Ares does *not* read your iMessage database. He reads the **Digital Spirit JSON** exported from Jarvis.
*   **Result**: Ares "knows" you like hiking because you told him via the Spirit file, not because he snooped on your texts.

## Workflow: How to run this

1.  **Start the Brain (on Jarvis)**
    *   Install **Ollama** (https://ollama.com).
    *   Run `ollama run llama3` in your terminal. This wakes up the AI.

2.  **Run the Triage App**
    *   Use the `start_jarvis.sh` script included in this repo.
    *   Go to `http://localhost:8000`.

3.  **Process Data**
    *   The app will eventually ingest your data and propose inferences.
    *   **Swipe Right (Approve)** on things that feel "true" to you.

4.  **Alchemy (Export)**
    *   Click the **"Export Spirit"** button in the app.
    *   This downloads a file: `ares_consciousness.json`.

5.  **Awaken Ares**
    *   Upload `ares_consciousness.json` to your VPS.
    *   Ares loads this into his memory (Vector DB or System Prompt) and instantly "becomes" you.

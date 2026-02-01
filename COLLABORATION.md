# Collaboration Guide: Orchestrating Your AI Agents

This guide answers your questions on how to manage a team of AI agents (Gemini, Claude, Grok, ChatGPT, etc.) working on this repository without stepping on each other's toes.

## 1. Should I make this GitHub Public?

**Verdict: Yes, but with strict safety measures.**

**Why Public?**
*   **Access:** Web-browsing agents (ChatGPT, Gemini, Perplexity) can instantly read your public code to understand the context. You can just paste the URL.
*   **Speed:** It removes the friction of uploading zip files or copy-pasting code blocks to every agent.

**⚠️ CRITICAL SAFETY WARNING ⚠️**
Since this project involves your *personal digital spirit* (iMessage, Notes, etc.), you must ensure **PRIVATE DATA NEVER REACHES GITHUB**.
*   **Check your `.gitignore`**: We have already configured it to ignore `inferences.json` and `*.db`. Never remove these lines.
*   **API Keys**: Never commit `.env` files or hardcoded keys.
*   **Personal Info**: Do not put your actual phone number or address in the `mock_data.py`.

## 2. What is a "Pull Request" (PR)?

Think of a Pull Request as a **"Staging Area"** or a **"Change Proposal"**.

1.  **The Branch**: An agent (or you) creates a copy of the code to work on a specific feature (e.g., `feature/add-neo4j`).
2.  **The Commit**: Changes are saved to that branch.
3.  **The Pull Request**: A request to merge that branch back into the `main` codebase.

**Your Role as the Human**:
You are the **Gatekeeper**. Agents write the code, but you review the PR. You check:
*   "Does this actually run?"
*   "Did it break the old features?"
*   "Is it trying to do something I didn't ask for?"
*   **Merge**: If it looks good, you click "Merge", and it becomes part of the official `main` code.

## 3. How to Achieve "Unity" (Speed & De-duplication)

The biggest problem with using multiple LLMs is **Context Fragmentation**. Claude doesn't know what ChatGPT just wrote.

### Strategy: "The Repo is the Source of Truth"

To stop agents from redoing work:

#### A. The "Context File" (`AGENTS.md` or `CURRENT_STATUS.md`)
Create a file specifically for the agents to read. Update it before starting a session.
*   **Example Content**:
    ```markdown
    # Current Status
    - Backend is done (FastAPI).
    - Frontend is done (HTML/JS).
    - CURRENT GOAL: Connect SQLite database.
    - DO NOT: Rewrite the CSS (it is finished).
    ```

#### B. Assign Roles (Specialization)
Treat your LLMs like a specialized software team. Don't ask everyone to do everything.
*   **Claude/Codex**: "You are the Senior Architect. Review this code and write the complex backend logic."
*   **ChatGPT/Grok**: "You are the Product Manager. Read the code and tell me what features are missing based on my goals."
*   **Gemini**: "You are the QA. Write tests for the code Claude just wrote."

#### C. The Workflow Loop
1.  **Pull** the latest `main` branch to your local machine.
2.  **Paste** the relevant files (or GitHub URL) to Agent A.
3.  **Agent A** writes code.
4.  **You** commit that code to Git immediately.
5.  **Paste** the *new* updated state to Agent B for the next step.

**Rule of Thumb**: Never let two agents work on the same file at the same time.

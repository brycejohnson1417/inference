# Inference Triage Program

## Overview
This application is a "Tinder for Inferences" triage tool. It is designed to help you rapidly validate the insights your local AI extracts from your personal data (iMessage, Notes, Social Media exports).

## Features
*   **Triage Interface**: Swipe-like interface to Approve (True) or Reject (False) inferences.
*   **Context Aware**: Shows the source data (e.g., the text message) alongside the AI's conclusion.
*   **JSON Persistence**: Saves your validated knowledge graph components for later use by your "Ares" agent.

## Getting Started

### Prerequisites
*   Python 3.10+
*   `pip`

### Installation
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage
1.  **Generate Mock Data** (To see how it works):
    ```bash
    python scripts/generate_mock_data.py
    ```
    *This creates a `inferences.json` file with sample connections (e.g., linking iMessage mentions to Instagram profiles).*

2.  **Start the Server**:
    ```bash
    uvicorn app.main:app --reload
    ```

3.  **Open the App**:
    Navigate to `http://localhost:8000` in your browser.

4.  **Triage**:
    *   **Green Check**: The inference is correct.
    *   **Red Cross**: The inference is incorrect.
    *   **Edit**: Add nuances or correct the details.

## Roadmap
*   Integrate real data ingestors for iMessage (`chat.db`).
*   Connect to Neo4j for robust Knowledge Graph storage.

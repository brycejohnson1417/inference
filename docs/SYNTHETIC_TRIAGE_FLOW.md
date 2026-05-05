# Synthetic Inference Triage Flow

This walkthrough uses generated mock data only. It is safe for a public demo because it does not rely on personal exports, private messages, contact records, browser history, or real knowledge files.

## Before Review

| Source | Evidence Snippet | Proposed Inference | Confidence |
|---|---|---|---|
| Messages + Social Export | A synthetic message mentions "Casey" and a synthetic social export includes `@casey_demo`. | The "Casey" in the message likely maps to `@casey_demo`. | 85% |
| Notes + Email | A synthetic note mentions a gift idea and a synthetic receipt mentions a related item. | A family member may be interested in gardening. | 90% |
| Chat Export | A synthetic prompt asks about fixing a home fixture. | The user may handle small home repairs. | 70% |

## Review Step

Each proposed inference is treated as untrusted until reviewed.

| Action | What It Means | Output |
|---|---|---|
| Reject | The claim is incorrect, too speculative, or not useful. | It is kept out of approved exports. |
| Edit | The claim is directionally useful but needs clarification. | Reviewer notes are attached before approval. |
| Approve | The claim is useful enough to become durable knowledge. | It becomes eligible for export. |

## After Review

Approved inferences can be exported as a small, structured knowledge file. The export route scans approved payloads for likely secrets before returning data.

Rejected and pending items stay out of the exported result.

## Why This Matters

AI-generated memory should not be accepted automatically. The useful product boundary is the review layer: the system proposes, the reviewer decides, and only approved claims become durable knowledge.

# Inference Triage Roadmap

This roadmap keeps the project focused on a local-first review loop for AI-generated claims.

## Product Direction

The core product idea is not automatic memory. It is controlled memory: generated claims should be reviewed, corrected, or rejected before they become durable knowledge.

## Near-Term Improvements

1. Improve the triage interface with clearer progress state, keyboard shortcuts, and batch review.
2. Add source-level permissions so each ingestor has an explicit data boundary.
3. Add entity confirmation cards for possible cross-source matches.
4. Store inference lineage so every approved claim can point back to synthetic or local-only evidence.
5. Expand export safety checks beyond simple secret-pattern heuristics.

## Architecture Themes

- Local-first processing for sensitive source material.
- Human-in-the-loop review before persistence.
- Synthetic public demo mode.
- Exported knowledge should be smaller and safer than raw source data.
- Ambiguous claims should stay pending instead of being treated as facts.

## Production Requirements

A production version would need:

- authentication
- encrypted local storage
- per-source import permissions
- audit logs
- retention controls
- stronger data-loss prevention
- source deletion and revocation flows
- clear review history for edited claims

## Demo Principle

Use generated mock data for public demos. The public value is the workflow, architecture, and safety boundary, not the underlying private data that a local-first version could process.

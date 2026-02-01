-- Core tables for the system

CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    canonical_name TEXT,
    entity_type TEXT,  -- person, place, org, concept
    created_at TIMESTAMP,
    metadata JSON
);

CREATE TABLE entity_aliases (
    alias TEXT,
    entity_id TEXT REFERENCES entities(id),
    source TEXT,
    confidence FLOAT
);

CREATE TABLE entity_relationships (
    entity_a TEXT REFERENCES entities(id),
    entity_b TEXT REFERENCES entities(id),
    relationship_type TEXT,
    strength FLOAT,
    evidence_ids JSON,
    updated_at TIMESTAMP
);

CREATE TABLE inferences (
    id TEXT PRIMARY KEY,
    type TEXT,
    statement TEXT,
    confidence FLOAT,
    weight FLOAT,
    source_ids JSON,
    entity_ids JSON,
    validation_status TEXT,
    created_at TIMESTAMP,
    validated_at TIMESTAMP,
    last_reinforced_at TIMESTAMP,
    version INTEGER DEFAULT 1,
    parent_inference_id TEXT  -- For inference evolution tracking
);

CREATE TABLE feedback_log (
    id TEXT PRIMARY KEY,
    inference_id TEXT REFERENCES inferences(id),
    decision TEXT,  -- approved, rejected, edited
    original_statement TEXT,
    edited_statement TEXT,
    decision_time_seconds FLOAT,  -- How long user took to decide
    created_at TIMESTAMP
);

CREATE TABLE contradictions (
    id TEXT PRIMARY KEY,
    inference_id TEXT REFERENCES inferences(id),
    conflicting_data_id TEXT,
    conflict_type TEXT,
    resolution TEXT,  -- pending, inference_updated, inference_invalidated, data_ignored
    created_at TIMESTAMP
);

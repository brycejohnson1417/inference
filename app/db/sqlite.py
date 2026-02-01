"""SQLite persistence layer.

Design goals:
- zero external deps (stdlib only)
- safe defaults: local file only
- keep API compatible with existing frontend fields

We store:
- inferences (triage candidates)
- raw_data_items (ingested raw snippets)

This is not the final schema for the full project, but it is a durable
stepping-stone vs JSON files.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.models import RawDataItem


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    return con


def init_db(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_items (
          id TEXT PRIMARY KEY,
          source TEXT NOT NULL,
          content TEXT NOT NULL,
          timestamp TEXT NOT NULL,
          metadata_json TEXT
        );
        """
    )

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS inferences (
          id TEXT PRIMARY KEY,
          source TEXT NOT NULL,
          content TEXT NOT NULL,
          inference TEXT NOT NULL,
          confidence REAL NOT NULL,
          status TEXT NOT NULL DEFAULT 'pending',
          user_notes TEXT,
          created_at TEXT NOT NULL
        );
        """
    )
    con.commit()


# -------------------------- Raw items --------------------------

def upsert_raw_items(con: sqlite3.Connection, items: Iterable[RawDataItem]) -> int:
    rows = 0
    for item in items:
        con.execute(
            """
            INSERT INTO raw_items(id, source, content, timestamp, metadata_json)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              source=excluded.source,
              content=excluded.content,
              timestamp=excluded.timestamp,
              metadata_json=excluded.metadata_json
            """,
            (
                item.id,
                item.source,
                item.content,
                item.timestamp.isoformat(),
                json.dumps(item.metadata or {}, ensure_ascii=False),
            ),
        )
        rows += 1
    con.commit()
    return rows


def list_raw_items(con: sqlite3.Connection, limit: int = 1000) -> List[Dict[str, Any]]:
    cur = con.execute(
        "SELECT id, source, content, timestamp, metadata_json FROM raw_items ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    )
    out: List[Dict[str, Any]] = []
    for r in cur.fetchall():
        md = {}
        try:
            md = json.loads(r["metadata_json"]) if r["metadata_json"] else {}
        except Exception:
            md = {}
        out.append(
            {
                "id": r["id"],
                "source": r["source"],
                "content": r["content"],
                "timestamp": r["timestamp"],
                "metadata": md,
            }
        )
    return out


# -------------------------- Inferences --------------------------

def insert_inference(
    con: sqlite3.Connection,
    *,
    inference_id: str,
    source: str,
    content: str,
    inference: str,
    confidence: float,
    status: str = "pending",
    user_notes: Optional[str] = None,
) -> None:
    con.execute(
        """
        INSERT INTO inferences(id, source, content, inference, confidence, status, user_notes, created_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            inference_id,
            source,
            content,
            inference,
            float(confidence),
            status,
            user_notes,
            datetime.utcnow().isoformat(),
        ),
    )
    con.commit()


def get_next_pending_inference(con: sqlite3.Connection) -> Optional[Dict[str, Any]]:
    cur = con.execute(
        """
        SELECT id, source, content, inference, confidence, status, user_notes
        FROM inferences
        WHERE status='pending'
        ORDER BY created_at ASC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    return dict(row) if row else None


def update_inference_status(con: sqlite3.Connection, inference_id: str, status: str, notes: Optional[str]) -> bool:
    cur = con.execute(
        """
        UPDATE inferences
        SET status=?, user_notes=COALESCE(?, user_notes)
        WHERE id=?
        """,
        (status, notes, inference_id),
    )
    con.commit()
    return cur.rowcount > 0


def list_inferences(con: sqlite3.Connection, status: Optional[str] = None) -> List[Dict[str, Any]]:
    if status:
        cur = con.execute(
            "SELECT id, source, content, inference, confidence, status, user_notes FROM inferences WHERE status=? ORDER BY created_at ASC",
            (status,),
        )
    else:
        cur = con.execute(
            "SELECT id, source, content, inference, confidence, status, user_notes FROM inferences ORDER BY created_at ASC"
        )
    return [dict(r) for r in cur.fetchall()]


# -------------------------- Migration helpers --------------------------

def import_legacy_json_inferences(con: sqlite3.Connection, json_path: Path) -> int:
    if not json_path.exists():
        return 0
    try:
        data = json.loads(json_path.read_text())
    except Exception:
        return 0
    if not isinstance(data, list):
        return 0

    inserted = 0
    for item in data:
        try:
            inference_id = str(item.get("id"))
            source = str(item.get("source"))
            content = str(item.get("content"))
            inference = str(item.get("inference"))
            confidence = float(item.get("confidence", 0.0))
            status = str(item.get("status", "pending"))
            user_notes = item.get("user_notes")
            # Avoid duplicates
            cur = con.execute("SELECT 1 FROM inferences WHERE id=?", (inference_id,))
            if cur.fetchone():
                continue
            insert_inference(
                con,
                inference_id=inference_id,
                source=source,
                content=content,
                inference=inference,
                confidence=confidence,
                status=status,
                user_notes=user_notes,
            )
            inserted += 1
        except Exception:
            continue

    return inserted

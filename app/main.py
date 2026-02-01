import json
import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import config
from app.brain import brain  # Import the Brain
from app.db import sqlite as db_sqlite
from app.ingestors.chatgpt import ChatGPTIngestor
from app.ingestors.safari import SafariIngestor

app = FastAPI()

# --- Configuration ---
# Prefer SQLite for durability. Keep legacy JSON paths for import/fallback.
SQLITE_PATH = config.SQLITE_PATH
DATA_FILE = str(config.INFERENCES_JSON_PATH)
RAW_DATA_FILE = str(config.RAW_DATA_JSON_PATH)

# --- Models ---
class IngestRequest(BaseModel):
    path: str

class Inference(BaseModel):
    id: str
    source: str  # e.g., "iMessage", "Instagram"
    content: str  # The raw text or data snippet
    inference: str  # The AI's conclusion
    confidence: float
    status: str = "pending"  # pending, approved, rejected
    user_notes: Optional[str] = None

class TriageRequest(BaseModel):
    id: str
    action: str  # "approve", "reject"
    notes: Optional[str] = None

# --- Data Manager ---
class InferencesDB:
    def __init__(self, filename):
        self.filename = filename
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump([], f)

    def load_all(self) -> List[dict]:
        with open(self.filename, "r") as f:
            return json.load(f)

    def save_all(self, data: List[dict]):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)

    def get_pending(self) -> Optional[dict]:
        data = self.load_all()
        for item in data:
            if item.get("status") == "pending":
                return item
        return None

    def update_status(self, inference_id: str, status: str, notes: str = None):
        data = self.load_all()
        found = False
        for item in data:
            if item["id"] == inference_id:
                item["status"] = status
                if notes:
                    item["user_notes"] = notes
                found = True
                break

        if found:
            self.save_all(data)
        return found

# --- Persistence ---
con = db_sqlite.connect(SQLITE_PATH)
db_sqlite.init_db(con)
# One-time best-effort import of legacy JSON inferences so existing users keep state.
db_sqlite.import_legacy_json_inferences(con, config.INFERENCES_JSON_PATH)

db = InferencesDB(DATA_FILE)

# --- Routes ---

# Serve Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/inference")
async def get_next_inference():
    inference = db_sqlite.get_next_pending_inference(con)
    if not inference:
        return {"message": "No pending inferences"}
    return inference

@app.post("/api/triage")
async def triage_inference(request: TriageRequest):
    new_status = "approved" if request.action == "approve" else "rejected"
    success = db_sqlite.update_inference_status(con, request.id, new_status, request.notes)
    if not success:
        raise HTTPException(status_code=404, detail="Inference not found")
    return {"status": "success"}

@app.get("/api/export")
async def export_consciousness():
    """Export all APPROVED inferences for Ares."""
    spirit_data = db_sqlite.list_inferences(con, status="approved")

    return JSONResponse(
        content=spirit_data,
        headers={"Content-Disposition": "attachment; filename=ares_consciousness.json"},
    )

@app.post("/api/generate")
async def trigger_generation():
    """Trigger the Brain to generate a new inference (manual trigger for now)."""
    new_inference = await brain.generate_inference("Random Source", "Random content snippet...")

    db_sqlite.insert_inference(
        con,
        inference_id=new_inference["id"],
        source=new_inference["source"],
        content=new_inference["content"],
        inference=new_inference["inference"],
        confidence=new_inference.get("confidence", 0.0),
        status=new_inference.get("status", "pending"),
    )

    return {"status": "generated", "id": new_inference["id"]}

@app.post("/api/ingest/{source}")
async def trigger_ingest(source: str, request: IngestRequest):
    """Trigger ingestion for a specific source."""
    if source == "chatgpt":
        ingestor = ChatGPTIngestor(request.path)
    elif source == "safari":
        ingestor = SafariIngestor(request.path)
    else:
        raise HTTPException(status_code=400, detail="Unknown source")

    items = ingestor.ingest()

    # Persist to SQLite (primary)
    stored = db_sqlite.upsert_raw_items(con, items)

    # Also persist to legacy raw_data.json for now (compat/debug)
    raw_data = []
    if os.path.exists(RAW_DATA_FILE):
        try:
            with open(RAW_DATA_FILE, "r") as f:
                raw_data = json.load(f)
        except Exception:
            raw_data = []

    new_items = [item.dict() for item in items]
    raw_data.extend(new_items)

    with open(RAW_DATA_FILE, "w") as f:
        json.dump(raw_data, f, indent=2, default=str)

    return {"status": "success", "source": source, "items_count": len(items), "stored": stored}

@app.post("/api/process")
async def process_raw_data():
    """Trigger the Brain to process raw data and generate triage inferences."""

    # Prefer SQLite raw items; fall back to legacy json.
    raw_items = db_sqlite.list_raw_items(con, limit=config.PROCESS_BATCH_SIZE)
    if not raw_items and os.path.exists(RAW_DATA_FILE):
        with open(RAW_DATA_FILE, "r") as f:
            raw_items = json.load(f)

    if not raw_items:
        return {"status": "no_data", "inferences_generated": 0}

    generated_count = 0

    # Process batch
    for item in raw_items[: config.PROCESS_BATCH_SIZE]:
        inference = await brain.generate_inference(item["source"], item["content"])
        db_sqlite.insert_inference(
            con,
            inference_id=inference["id"],
            source=inference["source"],
            content=inference["content"],
            inference=inference["inference"],
            confidence=inference.get("confidence", 0.0),
            status=inference.get("status", "pending"),
        )
        generated_count += 1

    return {"status": "success", "inferences_generated": generated_count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)

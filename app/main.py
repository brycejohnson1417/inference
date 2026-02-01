import json
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.brain import brain  # Import the Brain
from app.ingestors.chatgpt import ChatGPTIngestor
from app.ingestors.safari import SafariIngestor
from app.security import safe_to_export

app = FastAPI()

# --- Configuration ---
DATA_FILE = "inferences.json"
RAW_DATA_FILE = "raw_data.json"

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
    inference = db.get_pending()
    if not inference:
        return {"message": "No pending inferences"}
    return inference

@app.post("/api/triage")
async def triage_inference(request: TriageRequest):
    new_status = "approved" if request.action == "approve" else "rejected"
    success = db.update_status(request.id, new_status, request.notes)
    if not success:
        raise HTTPException(status_code=404, detail="Inference not found")
    return {"status": "success"}

@app.get("/api/export")
async def export_consciousness():
    """Export all APPROVED inferences for Ares.

    Security: This endpoint blocks export if the payload appears to contain secrets
    (API keys, tokens, private keys, etc.).
    """
    all_data = db.load_all()

    # Filter for approved inferences
    spirit_data = [item for item in all_data if item.get("status") == "approved"]

    # Gate export: scan serialized payload for common secret patterns.
    ok, hits = safe_to_export(json.dumps(spirit_data, ensure_ascii=False))
    if not ok:
        # Do NOT include raw matches; only a count.
        raise HTTPException(
            status_code=400,
            detail=f"Blocked export: detected {len(hits)} potential secret(s) in approved inferences. Please sanitize and try again.",
        )

    return JSONResponse(
        content=spirit_data,
        headers={"Content-Disposition": "attachment; filename=ares_consciousness.json"},
    )

@app.post("/api/generate")
async def trigger_generation():
    """Trigger the Brain to generate a new inference (Manual trigger for now)."""
    # In a real app, this would loop through the database.
    # Here we just generate one random mock/AI inference.
    new_inference = await brain.generate_inference("Random Source", "Random content snippet...")

    # Save to DB
    all_data = db.load_all()
    all_data.append(new_inference)
    db.save_all(all_data)

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

    # Persist to raw data file
    raw_data = []
    if os.path.exists(RAW_DATA_FILE):
        try:
            with open(RAW_DATA_FILE, "r") as f:
                raw_data = json.load(f)
        except:
            pass

    # Convert Pydantic models to dicts
    new_items = [item.dict() for item in items]

    # Append new items (simple append for now, duplicates possible)
    # In a real system, we'd check IDs
    raw_data.extend(new_items)

    with open(RAW_DATA_FILE, "w", default=str) as f:
        # custom serializer for datetime if needed, or rely on pydantic .dict() handling it mostly?
        # Actually pydantic .dict() keeps datetime objects which json.dump fails on.
        # We need to serialize properly.
        json.dump(raw_data, f, indent=2, default=str)

    return {"status": "success", "source": source, "items_count": len(items)}

@app.post("/api/process")
async def process_raw_data():
    """Trigger the Brain to process all raw data."""
    if not os.path.exists(RAW_DATA_FILE):
        return {"status": "no_data", "inferences_generated": 0}

    with open(RAW_DATA_FILE, "r") as f:
        raw_items = json.load(f)

    generated_count = 0
    new_inferences = []

    # Process batch (limit to 5 for now to avoid freezing)
    for item in raw_items[:5]:
        # Skip if we already have an inference for this content? (Simplification: process all)

        # Call Brain
        # Use brain.process_raw_data logic (we need to update brain.py first or inline it here)
        # Let's use the existing generate_inference method for now
        inference = await brain.generate_inference(item["source"], item["content"])
        new_inferences.append(inference)
        generated_count += 1

    # Save Inferences
    all_data = db.load_all()
    all_data.extend(new_inferences)
    db.save_all(all_data)

    return {"status": "success", "inferences_generated": generated_count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

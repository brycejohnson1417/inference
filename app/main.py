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

app = FastAPI()

# --- Configuration ---
DATA_FILE = "inferences.json"

# --- Models ---
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
    """Export all APPROVED inferences for Ares."""
    all_data = db.load_all()
    # Filter for approved inferences
    spirit_data = [item for item in all_data if item.get("status") == "approved"]

    return JSONResponse(
        content=spirit_data,
        headers={"Content-Disposition": "attachment; filename=ares_consciousness.json"}
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
async def trigger_ingest(source: str):
    """Trigger ingestion for a specific source."""
    # Placeholder for connection to real data files
    if source == "chatgpt":
        ingestor = ChatGPTIngestor("/path/to/export")
        # items = ingestor.ingest()
        return {"status": "ingestion_started", "source": source, "items_count": 0}
    elif source == "safari":
        ingestor = SafariIngestor()
        # items = ingestor.ingest()
        return {"status": "ingestion_started", "source": source, "items_count": 0}
    else:
        raise HTTPException(status_code=400, detail="Unknown source")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

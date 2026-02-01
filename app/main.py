import json
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

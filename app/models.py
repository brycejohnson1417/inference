from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime

class RawDataItem(BaseModel):
    id: str
    source: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class TemporalContext(BaseModel):
    timestamp: datetime
    day_of_week: str
    time_of_day: str
    season_of_life: Optional[str] = None
    active_projects: List[str] = []

class Inference(BaseModel):
    id: str
    type: str  # e.g., "preference", "relationship", "archetype_pattern"
    statement: str
    confidence: float
    source_ids: List[str]
    entity_ids: List[str] = []
    status: str = "pending"
    created_at: datetime = datetime.now()
    metadata: Optional[Dict[str, Any]] = None

class InferenceUpdate(BaseModel):
    action: str  # "supersede", "refine", "reinforce", "none"
    new_inference: Optional[Inference] = None
    reason: Optional[str] = None

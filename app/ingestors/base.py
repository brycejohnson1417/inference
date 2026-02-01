from typing import List, Any
from app.models import RawDataItem

class BaseIngestor:
    def __init__(self, source_path: str):
        self.source_path = source_path

    def ingest(self) -> List[RawDataItem]:
        raise NotImplementedError("Subclasses must implement ingest()")

from typing import List
from app.ingestors.base import BaseIngestor
from app.models import RawDataItem

class SafariIngestor(BaseIngestor):
    """
    Ingests Safari browsing history.
    """

    def ingest(self) -> List[RawDataItem]:
        # Placeholder for real logic
        # Would read History.db
        return []

    def categorize_url(self, url: str) -> str:
        """Categorize URL by type"""
        if "github.com" in url: return "dev"
        if "youtube.com" in url: return "video"
        return "other"

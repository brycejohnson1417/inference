from typing import List
import sqlite3
import os
import datetime
from app.ingestors.base import BaseIngestor
from app.models import RawDataItem

class SafariIngestor(BaseIngestor):
    """
    Ingests Safari browsing history.
    Expects source_path to be the full path to 'History.db'.
    """

    def ingest(self) -> List[RawDataItem]:
        if not os.path.exists(self.source_path):
            print(f"Error: {self.source_path} not found.")
            return []

        raw_items = []
        try:
            # Connect to the database
            # We use 'file:...' URI to open in read-only mode to prevent locking if Safari is open
            conn = sqlite3.connect(f"file:{self.source_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Query history items and visits
            # Safari stores time as Core Data timestamp (seconds since 2001-01-01)
            query = """
                SELECT
                    history_items.id,
                    history_items.url,
                    history_visits.visit_time,
                    history_visits.title
                FROM history_items
                JOIN history_visits ON history_items.id = history_visits.history_item
                ORDER BY history_visits.visit_time DESC
                LIMIT 1000
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                item_id, url, visit_time_core_data, title = row

                # Convert Core Data timestamp (2001 epoch) to Unix timestamp (1970 epoch)
                # 978307200 is the difference in seconds between 1970 and 2001
                unix_timestamp = visit_time_core_data + 978307200
                timestamp = datetime.datetime.fromtimestamp(unix_timestamp)

                if not title:
                    title = "No Title"

                category = self.categorize_url(url)

                item = RawDataItem(
                    id=f"safari_{item_id}_{int(unix_timestamp)}",
                    source="safari",
                    content=f"{title} - {url}",
                    timestamp=timestamp,
                    metadata={
                        "url": url,
                        "category": category,
                        "title": title
                    }
                )
                raw_items.append(item)

            conn.close()

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return []

        return raw_items

    def categorize_url(self, url: str) -> str:
        """Categorize URL by type"""
        if "github.com" in url or "stackoverflow.com" in url: return "dev"
        if "youtube.com" in url or "netflix.com" in url: return "video"
        if "google.com" in url and "search" in url: return "search"
        if "wikipedia.org" in url: return "research"
        if "amazon.com" in url: return "shopping"
        return "other"

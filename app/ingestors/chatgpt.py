from typing import List
from app.ingestors.base import BaseIngestor
from app.models import RawDataItem

class ChatGPTIngestor(BaseIngestor):
    """
    Ingests ChatGPT data export.
    """

    def ingest(self) -> List[RawDataItem]:
        # Placeholder for real logic
        # Would parse conversations.json
        return []

    def detect_frustration(self, prompt: str) -> List[str]:
        """Detect signals of user frustration in prompts"""
        signals = []
        frustration_patterns = [
            ("no that's not what i meant", "clarification"),
            ("try again", "retry_request"),
            ("you're not understanding", "comprehension_complaint"),
        ]
        prompt_lower = prompt.lower()
        for pattern, signal_type in frustration_patterns:
            if pattern in prompt_lower:
                signals.append(signal_type)
        return signals

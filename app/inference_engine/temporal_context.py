from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

@dataclass
class TemporalContext:
    """Rich context about when something happened"""
    timestamp: datetime
    day_of_week: str
    time_of_day: str  # "morning", "afternoon", "evening", "night"

    # What else was happening
    calendar_events: List[str]  # Events within 2 hours
    recent_messages: int  # Message volume in last hour
    recent_searches: List[str]  # What they searched recently

    # Life context
    season_of_life: str  # Inferred from recent patterns
    active_projects: List[str]  # From project tracking
    stress_indicators: float  # Inferred from patterns

class TemporalContextBuilder:
    """Builds rich temporal context for any data point"""

    def __init__(self, data_sources: dict):
        self.sources = data_sources

    def build_context(self, timestamp: datetime) -> TemporalContext:
        """Build context for a specific moment in time"""
        # Placeholder logic
        return TemporalContext(
            timestamp=timestamp,
            day_of_week=timestamp.strftime("%A"),
            time_of_day="unknown",
            calendar_events=[],
            recent_messages=0,
            recent_searches=[],
            season_of_life="unknown",
            active_projects=[],
            stress_indicators=0.0
        )

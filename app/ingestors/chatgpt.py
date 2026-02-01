from typing import List
import json
import os
import datetime
from app.ingestors.base import BaseIngestor
from app.models import RawDataItem

class ChatGPTIngestor(BaseIngestor):
    """
    Ingests ChatGPT data export.
    Expects source_path to be the directory containing 'conversations.json'.
    """

    def ingest(self) -> List[RawDataItem]:
        conversations_file = os.path.join(self.source_path, "conversations.json")
        if not os.path.exists(conversations_file):
            print(f"Error: {conversations_file} not found.")
            return []

        try:
            with open(conversations_file, "r") as f:
                conversations = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {conversations_file}")
            return []

        raw_items = []
        for convo in conversations:
            convo_id = convo.get("id", "unknown")
            mapping = convo.get("mapping", {})

            # Iterate through messages in the conversation
            for msg_id, msg_data in mapping.items():
                message = msg_data.get("message")
                if not message:
                    continue

                author = message.get("author", {})
                role = author.get("role")

                # We care about USER prompts to analyze the user
                if role == "user":
                    content_parts = message.get("content", {}).get("parts", [])
                    text_content = " ".join([str(p) for p in content_parts if isinstance(p, str)])

                    if not text_content.strip():
                        continue

                    create_time = message.get("create_time")
                    timestamp = datetime.datetime.now()
                    if create_time:
                        timestamp = datetime.datetime.fromtimestamp(create_time)

                    # Detect frustration
                    frustration_signals = self.detect_frustration(text_content)

                    item = RawDataItem(
                        id=f"chatgpt_{msg_id}",
                        source="chatgpt",
                        content=text_content,
                        timestamp=timestamp,
                        metadata={
                            "conversation_id": convo_id,
                            "frustration_signals": frustration_signals,
                            "role": "user"
                        }
                    )
                    raw_items.append(item)

        return raw_items

    def detect_frustration(self, prompt: str) -> List[str]:
        """Detect signals of user frustration in prompts"""
        signals = []
        frustration_patterns = [
            ("no that's not what i meant", "clarification"),
            ("try again", "retry_request"),
            ("you're not understanding", "comprehension_complaint"),
            ("stop", "command_stop"),
            ("wrong", "correction")
        ]
        prompt_lower = prompt.lower()
        for pattern, signal_type in frustration_patterns:
            if pattern in prompt_lower:
                signals.append(signal_type)
        return signals

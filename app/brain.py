import httpx
import json
import uuid
import random
from typing import List, Dict, Any

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
# Use env var override so deployments can pin a specific local model.
# Default aligns with Bryce's briefing.
OLLAMA_MODEL = __import__("os").environ.get("OLLAMA_MODEL", "llama3.2:3b")

# Fallback Mock Data (if Ollama is offline)
MOCK_INFERENCES = [
    {
        "source": "iMessage",
        "content": "Message to Mom: 'I'll bring the vegan salad.'",
        "inference": "User prefers vegan food options.",
        "confidence": 0.88
    },
    {
        "source": "Notes",
        "content": "Note: 'Buy more filament for the Prusa.'",
        "inference": "User owns a 3D printer (Prusa).",
        "confidence": 0.95
    }
]

class Brain:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def is_alive(self) -> bool:
        """Check if Ollama is running."""
        try:
            resp = await self.client.get("http://localhost:11434/api/tags")
            return resp.status_code == 200
        except httpx.ConnectError:
            return False

    async def generate_inference(self, source: str, content: str) -> Dict[str, Any]:
        """
        Ask the Local LLM to infer a fact from the content.
        """
        if not await self.is_alive():
            # Fallback to mock logic if brain is offline
            # print("⚠️ Brain (Ollama) is offline. Using mock logic.")
            return self._mock_inference(source, content)

        prompt = f"""
        Analyze the following data source and content.
        Extract a single key fact or inference about the user.
        Return ONLY the inference text.

        Source: {source}
        Content: {content}
        Inference:
        """

        try:
            response = await self.client.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
            )
            response.raise_for_status()
            result = response.json()
            inference_text = result.get("response", "").strip()

            return {
                "id": str(uuid.uuid4()),
                "source": source,
                "content": content,
                "inference": inference_text,
                "confidence": 0.85, # Placeholder: Local LLMs don't always give confidence easily
                "status": "pending"
            }
        except Exception as e:
            print(f"Error calling brain: {e}")
            return self._mock_inference(source, content)

    def _mock_inference(self, source: str, content: str) -> Dict[str, Any]:
        """Generate a random mock inference."""
        template = random.choice(MOCK_INFERENCES)
        return {
            "id": str(uuid.uuid4()),
            "source": source,
            "content": content,
            "inference": template["inference"] + " (Mock)",
            "confidence": template["confidence"],
            "status": "pending"
        }

brain = Brain()

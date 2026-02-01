import json
import uuid

DATA_FILE = "inferences.json"

MOCK_INFERENCES = [
    {
        "id": str(uuid.uuid4()),
        "source": "iMessage + Instagram",
        "content": "iMessage: 'Hey, are you going to Sarah's party?' | Instagram: Found profile '@sarah_j' followed by mutuals.",
        "inference": "The 'Sarah' mentioned in text is likely Instagram user '@sarah_j'.",
        "confidence": 0.85,
        "status": "pending"
    },
    {
        "id": str(uuid.uuid4()),
        "source": "Facebook Export",
        "content": "Post: 'Loved the hiking trail at Yosemite!' (2019)",
        "inference": "User has a long-term interest in Hiking/Outdoors.",
        "confidence": 0.95,
        "status": "pending"
    },
    {
        "id": str(uuid.uuid4()),
        "source": "Notes App + Email",
        "content": "Note: 'Gift ideas for Mom: Gardening tools' | Email: Receipt from Home Depot for 'Shovel'.",
        "inference": "User's mother is interested in Gardening.",
        "confidence": 0.90,
        "status": "pending"
    },
    {
        "id": str(uuid.uuid4()),
        "source": "X Export",
        "content": "Retweet: 'New LLM paper dropped today!'",
        "inference": "User is interested in AI/Machine Learning research.",
        "confidence": 0.92,
        "status": "pending"
    },
    {
        "id": str(uuid.uuid4()),
        "source": "ChatGPT Export",
        "content": "Prompt: 'How to fix a leaky faucet'",
        "inference": "User handles DIY home repairs.",
        "confidence": 0.70,
        "status": "pending"
    }
]

def main():
    print(f"Generating {len(MOCK_INFERENCES)} mock inferences...")
    with open(DATA_FILE, "w") as f:
        json.dump(MOCK_INFERENCES, f, indent=2)
    print(f"Successfully wrote to {DATA_FILE}")

if __name__ == "__main__":
    main()

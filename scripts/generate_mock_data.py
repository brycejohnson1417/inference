import json
import uuid

DATA_FILE = "inferences.json"

MOCK_INFERENCES = [
    {
        "id": str(uuid.uuid4()),
        "source": "Messages + Social Export",
        "content": "Message: 'Hey, are you going to Casey's event?' | Social export: Found profile '@casey_demo' followed by mutuals.",
        "inference": "The 'Casey' mentioned in the message is likely social profile '@casey_demo'.",
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
        "content": "Note: 'Gift ideas for a family member: Gardening tools' | Email: Receipt from a hardware store for 'Shovel'.",
        "inference": "A family member is likely interested in gardening.",
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

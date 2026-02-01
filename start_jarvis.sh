#!/bin/bash

# start_jarvis.sh
# One-click launcher for the Digital Spirit Triage App on macOS

echo "🔮 Initializing Jarvis (Inference Triage)..."

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it (e.g., brew install python3)."
    exit 1
fi

# 2. Check for Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Activate Virtual Environment
source venv/bin/activate

# 4. Install Dependencies
echo "⬇️  Checking dependencies..."
pip install -r requirements.txt > /dev/null

# 5. Check for Brain (Ollama) - Optional check
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama (The Brain) is not running or not installed."
    echo "   You can still use the app with Mock Data, but real AI features won't work."
    echo "   To fix: Install Ollama from https://ollama.com and run 'ollama serve' in another terminal."
    echo ""
fi

# 6. Start the Server
echo "🚀 Starting Triage Interface..."
echo "👉 Open your browser to: http://localhost:8000"
echo "   (Press Ctrl+C to stop)"

# Run Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

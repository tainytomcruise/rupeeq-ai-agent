#!/bin/bash

# RupeeQ AI Calling Agent - Startup Script

echo "🚀 Starting RupeeQ AI Calling Agent..."
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "🔍 Checking dependencies..."
python -c "import flask, flask_socketio, speech_recognition, pyttsx3" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing requirements..."
    pip install -r requirements.txt
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Set environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1

echo "✅ Starting server..."
echo "📊 Dashboard: http://localhost:8080"
echo "🤖 AI Agent: http://localhost:8080/ai-agent"
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python run.py


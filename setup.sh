#!/bin/bash

# RupeeQ AI Calling Agent - Setup Script

echo "🚀 Setting up RupeeQ AI Calling Agent..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create database directory if it doesn't exist
mkdir -p data

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the application:"
echo "   source venv/bin/activate"
echo "   python3 run.py"
echo ""
echo "🌐 Then visit:"
echo "   Dashboard: http://localhost:8080"
echo "   AI Agent:  http://localhost:8080/ai-agent"
echo ""
echo "📚 For deployment instructions, see DEPLOYMENT.md"

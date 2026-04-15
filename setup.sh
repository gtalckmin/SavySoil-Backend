#!/bin/bash
# SavySoil Backend - Local Development Setup Script
# ===================================================
# This script sets up your local development environment for the SavySoil backend

set -e

echo "🌱 SavySoil Backend - Local Setup"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

echo "✅ Python $(python3 --version) found"
echo ""

# Navigate to backend directory
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BACKEND_DIR"

echo "📂 Working directory: $BACKEND_DIR"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"

echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔐 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  UPDATE .env WITH YOUR SETTINGS:"
    echo "   - GEMMA_API_KEY: Your LLM provider API key"
    echo "   - GEMMA_ENDPOINT: Your LLM endpoint URL"
    echo "   - GITHUB_PAGES_ORIGIN: http://localhost:3000 (for testing)"
    echo ""
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the development server, run:"
echo "  cd backend"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  uvicorn main:app --reload"
echo ""
echo "Then visit: http://localhost:8000/docs"
echo ""

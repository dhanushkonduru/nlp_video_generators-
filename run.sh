#!/bin/bash

# AI Educational Video Generator - Streamlit Server Wrapper
# This script ensures proper environment setup before launching Streamlit

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env and add your API keys:"
    echo "   - GROK_API_KEY: Get from https://console.x.ai/"
    echo "   - PEXELS_API_KEY: Get from https://www.pexels.com/api/"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

# Set environment variables for macOS stability
export PYTORCH_ENABLE_MPS_FALLBACK=1
export OMP_NUM_THREADS=1

# Verify FFmpeg installation
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found. Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "❌ Homebrew not found. Please install FFmpeg manually:"
        echo "   $ brew install ffmpeg"
        exit 1
    fi
fi

echo "✅ Environment ready. Starting Streamlit server..."
echo "🌐 Local URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Launch Streamlit
streamlit run streamlit_app.py "$@"

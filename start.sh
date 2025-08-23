#!/bin/bash

# CI/CD Fixer Agent Startup Script
# This script sets up and starts the CI/CD Fixer Agent with Portia integration

set -e

echo "🚀 Starting CI/CD Fixer Agent with Portia Integration"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the cicd_fixer_agent directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Please copy .env.example to .env and configure your environment variables"
    echo "   Required variables:"
    echo "     - GITHUB_TOKEN"
    echo "     - GOOGLE_API_KEY"
    echo "     - GITHUB_WEBHOOK_SECRET"
    echo "     - SECRET_KEY"
    echo "     - DATABASE_URL"
    echo ""
    echo "   Optional variables:"
    echo "     - PORTIA_API_KEY"
    echo "     - PORTIA_ENVIRONMENT"
    echo ""
    
    read -p "Do you want to continue without .env file? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Please configure .env file first."
        exit 1
    fi
fi

# Test Portia integration
echo "🧪 Testing Portia integration..."
if python scripts/test_portia.py; then
    echo "✅ Portia integration test passed"
else
    echo "⚠️  Portia integration test failed. Some features may not work correctly."
    echo "   Check the test output above for details."
fi

# Check if database is accessible
echo "🗄️  Checking database connection..."
if python -c "
import sys
sys.path.insert(0, 'src')
from cicd_fixer.database.connection import get_db_connection
db = get_db_connection()
if db.test_connection():
    print('✅ Database connection successful')
else:
    print('❌ Database connection failed')
    sys.exit(1)
"; then
    echo "✅ Database connection verified"
else
    echo "❌ Database connection failed"
    echo "   Please check your DATABASE_URL in .env file"
    echo "   You can run 'python scripts/setup_db.py' to set up the database"
fi

# Start the application
echo ""
echo "🎯 Starting CI/CD Fixer Agent..."
echo "   API will be available at: http://localhost:8000"
echo "   Documentation: http://localhost:8000/docs"
echo "   Health check: http://localhost:8000/health"
echo "   Portia test: http://localhost:8000/api/v1/portia/test"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python -m uvicorn cicd_fixer.main:app --host 0.0.0.0 --port 8000 --reload

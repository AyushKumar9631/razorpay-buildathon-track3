#!/bin/bash

# Quick setup script for test data generation

echo "=========================================="
echo "AI Revenue Recovery - Test Data Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Run this script from the project root directory"
    exit 1
fi

# Install Faker if needed
echo "Installing dependencies..."
pip install Faker --break-system-packages 2>/dev/null || pip install Faker

# Check database connection
echo ""
echo "Checking database connection..."
cd backend
python -c "from app.database import engine; engine.connect()" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Database connected"
else
    echo "⚠ Warning: Could not connect to database"
    echo "  Make sure DATABASE_URL is set in backend/.env"
fi

# Check OpenAI API key
python -c "from app.config import settings; assert settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your_openai_api_key_here'" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ OpenAI API key configured"
else
    echo "⚠ Warning: OpenAI API key not configured"
    echo "  Set OPENAI_API_KEY in backend/.env"
fi

cd ..

echo ""
echo "=========================================="
echo "Ready to generate test data!"
echo "=========================================="
echo ""
echo "Run the following commands:"
echo ""
echo "1. Generate test data:"
echo "   python scripts/generate_test_data.py"
echo ""
echo "2. Run AI simulation:"
echo "   python scripts/run_ai_simulation.py"
echo ""
echo "3. Start backend:"
echo "   cd backend && uvicorn app.main:app --reload"
echo ""

#!/bin/bash
# Quick setup script for Local Host Dashboard

set -e

echo "========================================"
echo "Local Host Dashboard - Setup Script"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Check for optional tools
echo "Checking for optional tools..."
if command -v smartctl &> /dev/null; then
    echo "✓ smartctl found (S.M.A.R.T monitoring enabled)"
else
    echo "⚠ smartctl not found (S.M.A.R.T monitoring disabled)"
    echo "  Install with: sudo apt-get install smartmontools"
fi
echo ""

# Make run script executable
chmod +x run.py
echo "✓ run.py is executable"
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the dashboard, run:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Then access it at: http://localhost:5000"
echo ""
echo "For network access from other machines:"
echo "  python run.py --host 0.0.0.0"
echo ""

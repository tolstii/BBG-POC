#!/bin/bash

# Setup script for Ownership Data Quality Assessment POC
# This script automates the installation and initial setup

set -e  # Exit on error

echo "=========================================="
echo "Ownership DQ POC - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Error: Python 3.9+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ Pip upgraded"
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Download spaCy model
echo "Downloading spaCy model for NLP..."
python -m spacy download en_core_web_sm
echo "✅ spaCy model downloaded"
echo ""

# Create necessary directories
echo "Creating project directories..."
mkdir -p data reports visualizations
echo "✅ Directories created"
echo ""

echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "To get started:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the pipeline: python -m ownership_dq.main"
echo "  3. Launch dashboard: streamlit run ownership_dq/dashboard.py"
echo ""
echo "For more information, see README.md"
echo ""

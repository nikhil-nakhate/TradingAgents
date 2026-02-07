#!/bin/bash
# Setup script for TradingAgents conda environment

set -e  # Exit on error

echo "========================================="
echo "TradingAgents Environment Setup"
echo "========================================="

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda not found. Please install Miniconda or Anaconda first."
    exit 1
fi

# Create conda environment
echo ""
echo "📦 Creating conda environment 'tradingagents' with Python 3.11..."
conda create -n tradingagents python=3.11 -y

# Activate environment
echo ""
echo "🔄 Activating environment..."
source /home/nikhil/miniconda3/bin/activate tradingagents

# Install requirements
echo ""
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Verify installation
echo ""
echo "✅ Verifying installation..."
python -c "import langchain; import yfinance; import langgraph; print('✓ Core packages installed successfully')"

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "To activate the environment, run:"
echo "  conda activate tradingagents"
echo ""
echo "To test the discovery feature, run:"
echo "  python test_discovery.py"
echo ""

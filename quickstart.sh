#!/bin/bash
# Quick Start Script for Climate KG Pipeline

echo "=============================================================================="
echo "Climate Knowledge Graph Pipeline - Quick Start"
echo "=============================================================================="

# Activate virtual environment
source venv/bin/activate

# Test installation
echo ""
echo "Step 1: Testing installation..."
python test_installation.py

if [ $? -ne 0 ]; then
    echo "❌ Installation test failed. Please check the errors above."
    exit 1
fi

echo ""
echo "=============================================================================="
echo "Step 2: Choose your action:"
echo "=============================================================================="
echo ""
echo "1. Run TEST mode (1 year, single variable - RECOMMENDED FIRST)"
echo "   python code/pipeline.py --test"
echo ""
echo "2. Process single variable for 1 year (small test)"
echo "   python code/pipeline.py --variables tg --start-year 2020 --end-year 2020"
echo ""
echo "3. Process temperature variables 2015-2024"
echo "   python code/pipeline.py --variables tg tn tx --start-year 2015 --end-year 2024"
echo ""
echo "4. Full production run (1950-2024, all variables)"
echo "   python code/pipeline.py --start-year 1950 --end-year 2024"
echo ""
echo "=============================================================================="
echo "Ready to proceed! Choose an option above or see code/README.md for details."
echo "=============================================================================="

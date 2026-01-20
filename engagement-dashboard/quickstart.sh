#!/bin/bash
# Quick Start Script for X Engagement Dashboard

echo "=================================="
echo "X Engagement Dashboard Quick Start"
echo "=================================="
echo ""
echo "Choose an option:"
echo ""
echo "1. Open Web Interface (recommended)"
echo "2. Run Python CLI Analyzer"
echo "3. Run Test Examples"
echo "4. View README"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Opening web interface..."
        echo ""
        echo "The index.html file should open in your default browser."
        echo "If it doesn't open automatically, navigate to:"
        echo "$(pwd)/index.html"
        echo ""
        if command -v xdg-open > /dev/null; then
            xdg-open index.html
        elif command -v open > /dev/null; then
            open index.html
        else
            echo "Please manually open: $(pwd)/index.html in your browser"
        fi
        ;;
    2)
        echo ""
        echo "Starting Python CLI Analyzer..."
        echo ""
        python3 analyzer.py
        ;;
    3)
        echo ""
        echo "Running test examples..."
        echo ""
        python3 test_examples.py
        ;;
    4)
        echo ""
        if command -v less > /dev/null; then
            less README.md
        else
            cat README.md
        fi
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

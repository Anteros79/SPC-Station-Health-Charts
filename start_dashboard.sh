#!/bin/bash
# Airline Tech Ops SPC Dashboard Launcher (macOS/Linux)
# This script starts the Python server and opens the dashboard

echo ""
echo "========================================================"
echo "  Airline Tech Ops SPC Dashboard"
echo "========================================================"
echo ""
echo "Starting Python server..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python from https://www.python.org"
    exit 1
fi

echo "Server will start on http://localhost:8000"
echo ""
echo "IMPORTANT: Keep this terminal open while using the dashboard!"
echo "Press Ctrl+C to stop the server when done."
echo ""
echo "Opening dashboard in your default browser..."
sleep 2

# Start Python server in background
python3 server.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Open the dashboard in default browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:8000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:8000
fi

echo ""
echo "Dashboard is now running in your browser!"
echo "Keep this terminal open. Press Ctrl+C to stop the server."
echo ""

# Wait for the server process
wait $SERVER_PID


#!/bin/bash
# Austin Maxi Bot - Linux/Mac Startup Script

echo ""
echo "========================================"
echo "  Austin Maxi Bot - Starting Services"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
    playwright install chromium
fi

# Activate venv
source venv/bin/activate

echo "Starting services..."
echo ""

# Start License Server
echo "Starting License Server (Port 5000)..."
python server.py &
LICENSE_PID=$!
sleep 2

# Start Signal Server
echo "Starting Signal Server (Port 5001)..."
python signal_bot.py &
SIGNAL_PID=$!
sleep 2

# Start Admin Bot
echo "Starting Admin Bot..."
python admin_bot.py &
ADMIN_PID=$!
sleep 2

# Start Client Bot
echo "Starting Client Bot..."
python client_bot.py &
CLIENT_PID=$!

echo ""
echo "========================================"
echo "All services started!"
echo "========================================"
echo ""
echo "License Server: http://localhost:5000"
echo "Signal Server:  http://localhost:5001"
echo ""
echo "Process IDs:"
echo "  License Server: $LICENSE_PID"
echo "  Signal Server:  $SIGNAL_PID"
echo "  Admin Bot:      $ADMIN_PID"
echo "  Client Bot:     $CLIENT_PID"
echo ""
echo "To stop all services, run:"
echo "  kill $LICENSE_PID $SIGNAL_PID $ADMIN_PID $CLIENT_PID"
echo ""

# Wait for all processes
wait

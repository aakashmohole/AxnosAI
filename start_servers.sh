#!/bin/bash

# Define cleanup procedure to stop all background processes on exit
cleanup() {
    echo ""
    echo "Stopping all servers..."
    # kill child processes
    kill $(jobs -p) 2>/dev/null
    exit
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

echo "Cleaning up lingering processes on ports 3000, 3001, 8000, 8001..."
lsof -ti:3000,3001,8000,8001 | xargs kill -9 2>/dev/null

echo "Pre-building data-sci-executor Docker image (for faster code execution)..."
(
    cd main-backend-service
    docker build -t data-sci-executor . &
)

echo "Starting main-backend-service (Port 8000)..."
(
    cd main-backend-service
    source venv/bin/activate
    python manage.py runserver
) &

echo "Starting proxy-orchestration-server (Port 8001)..."
(
    cd proxy-orchestration-server
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "venv2" ]; then
        source venv2/bin/activate
    fi
    uvicorn manage:app --port 8001 --reload
) &

echo "Starting auth-service..."
(
    cd auth-service
    npm run start:dev
) &

if [ -d "../Axnos-UI" ]; then
    echo "Starting Axnos-UI (Frontend)..."
    (
        cd ../Axnos-UI
        npm run dev
    ) &
fi

echo "=========================================="
echo "All servers are starting up!"
echo "Press Ctrl+C to stop all servers."
echo "=========================================="

# Wait for all background jobs to finish
wait

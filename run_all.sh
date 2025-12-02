#!/bin/bash

# Get the absolute path of the script directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to kill all background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    # Kill all child processes of this script
    pkill -P $$
    exit
}

# Trap Ctrl+C (SIGINT) and termination signals
trap cleanup SIGINT SIGTERM

echo "🚀 Initializing MLOps Project..."

# --- 1. Backend & MLflow ---
echo "🔹 Starting Backend and MLflow..."
cd "$PROJECT_ROOT/mlpos-shawarma-forecast/backend"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found! Please run setup first."
    exit 1
fi

source .venv/bin/activate

# Start FastAPI Backend in background
uvicorn app.main:app --reload --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!
echo "   ✅ Backend started (PID: $BACKEND_PID)"

# Start MLflow in background
mlflow ui --port 5001 > /dev/null 2>&1 &
MLFLOW_PID=$!
echo "   ✅ MLflow started (PID: $MLFLOW_PID)"

# --- 2. Frontend ---
echo "🔹 Starting Frontend..."
cd "$PROJECT_ROOT/mlpos-shawarma-forecast/frontend"

# Start Vite Frontend in background
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
echo "   ✅ Frontend started (PID: $FRONTEND_PID)"

# --- Summary ---
echo ""
echo "------------------------------------------------"
echo "🎉 All systems operational!"
echo ""
echo "📄 Swagger API:  http://localhost:8000/docs"
echo "💻 Frontend App: http://localhost:5173"
echo "🔬 MLflow UI:    http://localhost:5001"
echo "------------------------------------------------"
echo "Press Ctrl+C to stop all services."

# Wait for any process to exit
wait

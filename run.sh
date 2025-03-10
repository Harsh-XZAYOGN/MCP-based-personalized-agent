#!/bin/bash

# Start MongoDB if not running (adjust for your MongoDB setup)
echo "Checking MongoDB status..."
if ! pgrep -x "mongod" > /dev/null
then
    echo "Starting MongoDB..."
    mongod --dbpath ./data/db &
    sleep 5  # Give MongoDB time to start
fi

# Start FastAPI backend
echo "Starting FastAPI backend..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to initialize
echo "Waiting for backend to initialize..."
sleep 3

# Start Streamlit frontend
echo "Starting Streamlit frontend..."
streamlit run frontend/streamlit_app.py --server.port 8501

# Cleanup when script is terminated
trap "kill $BACKEND_PID; echo 'Shutting down services...'" EXIT

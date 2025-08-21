#!/bin/bash

# Start FastAPI backend in the background
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to start
sleep 5

# Start Streamlit frontend
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
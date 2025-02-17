#!/bin/sh

echo "Starting FastAPI server..."
exec uvicorn api.api:app --host 0.0.0.0 --port "$API_PORT"

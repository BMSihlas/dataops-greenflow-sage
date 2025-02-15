import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv, find_dotenv

# Load environment variables
if not find_dotenv():
    print("Warning: .env file not found. Ensure it exists before running this script.")
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="GreenFlow Sage API",
    description="API to serve sustainability insights from sensor data",
    version="1.0"
)

@app.get("/")
def root():
    """Root endpoint to check API health."""
    return {"message": "GreenFlow Sage API is running!"}

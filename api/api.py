import os
import sys
from fastapi import FastAPI, HTTPException, Header
from sqlalchemy.engine.base import Engine
from dotenv import load_dotenv, find_dotenv
from db.utils import get_db_engine, fetch_table_data
from db.load_data import main as deploy_parquet_data
from db.process_insights import main as process_insights

ENV_VARS: list[str] = ["API_SECRET_KEY"]

"""Loads environment variables and validates required ones."""
if not find_dotenv():
    print("Warning: .env file not found. Ensure it exists before running this script.")

load_dotenv()

# Validate required environment variables
missing_vars: list[str] = [var for var in ENV_VARS if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# Retrieve API Key from environment variables
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

# Initialize FastAPI app
app = FastAPI(
    title="GreenFlow Sage API",
    description="API to serve sustainability insights from sensor data",
    version="1.0"
)

def db_connect() -> Engine:
    return get_db_engine()

@app.get("/")
def root():
    """Root endpoint to check API health."""
    return {"message": "GreenFlow Sage API is running!"}

@app.get("/insights")
def get_insights():
    """Fetch sustainability insights from PostgreSQL."""
    try:
        engine = db_connect()

        insights_df = fetch_table_data(engine, "insights")
        if insights_df is None or insights_df.empty:
            raise HTTPException(status_code=404, detail="No insights found.")
        
        insights = insights_df.to_dict(orient="records")
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching insights: {str(e)}")

@app.get("/insights/{sector}")
def get_sector_insights(sector: str):
    """Fetch insights for a specific sector."""
    try:
        engine = db_connect()

        insights_df = fetch_table_data(engine, "insights")
        insights_df = insights_df[insights_df["sector"] == sector]

        if insights_df.empty:
            raise HTTPException(status_code=404, detail=f"No insights found for sector: {sector}")
        
        insights = insights_df.to_dict(orient="records")
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching insights for {sector}: {str(e)}")

@app.get("/sectors")
def get_sectors():
    """Fetch list of unique sectors from PostgreSQL."""
    try:
        engine = db_connect()

        insights_df = fetch_table_data(engine, "insights")
        sectors = insights_df["sector"].unique().tolist()

        return {"sectors": sectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sectors: {str(e)}")

@app.get("/sensor-data")
def get_sensor_data(limit: int = 10):
    """Fetch latest sensor data records from PostgreSQL."""
    try:
        engine = db_connect()

        sensor_data_df = fetch_table_data(engine, "sensor_data")

        if sensor_data_df is None or sensor_data_df.empty:
            raise HTTPException(status_code=404, detail="No sensor data found.")
        
        sensor_data = sensor_data_df.to_dict(orient="records")
        return {"sensor_data": sensor_data[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sensor data: {str(e)}")

@app.post("/load-data")
def load_data(x_api_key: str = Header(None)):
    """Secure API to load Parquet data into PostgreSQL."""
    if not x_api_key or x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    try:
        if deploy_parquet_data():
            if not process_insights():
                return {"message": "Failed to load processed insights into PostgreSQL."}
            else:
                return {"message": "Data successfully loaded into PostgreSQL."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")
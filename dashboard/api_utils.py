import requests
import pandas as pd
from config import API_BASE_URL

def fetch_sectors():
    """Fetch available sectors from API."""
    response = requests.get(f"{API_BASE_URL}/sectors")
    return response.json().get("sectors", []) if response.status_code == 200 else []

def fetch_sector_insights():
    """Fetch available sectors from API."""
    response = requests.get(f"{API_BASE_URL}/insights")
    return response.json().get("insights", []) if response.status_code == 200 else []

def fetch_companies_by_sector(sector, page=1, page_size=10, order_by=None, order_dir=None):
    """Fetch paginated list of companies with optional sector filter."""
    params = {
        "sector": None if sector == "All" else sector,
        "page": page,
        "page_size": page_size
    }
    if order_by is not None:
        params["order_by"] = order_by
        params["order_dir"] = order_dir is not None and order_dir == "desc" and order_dir or "asc"
    response = requests.get(f"{API_BASE_URL}/companies", params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("companies", []), data.get("total_pages", 1)
    return [], 1

def fetch_sensor_data(company, sector):
    """Fetch sensor data for a selected company and sector."""
    params = {
        "sector": None if sector == "All" else sector,
        "company": None if company == "All" else company
    }
    response = requests.get(f"{API_BASE_URL}/sensor-data", params=params)
    
    if response.status_code == 200:
        return pd.DataFrame(response.json().get("sensor_data", []))
    return pd.DataFrame()

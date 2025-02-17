import requests
import pandas as pd
from components.config import API_BASE_URL
from pydantic import BaseModel
from typing import Optional
import streamlit as st

def get_headers():
    """Retrieve authorization headers if user is authenticated."""
    token = st.session_state.get("jwt_token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def fetch_sectors():
    """Fetch available sectors from API."""
    response = requests.get(f"{API_BASE_URL}/sectors", headers=get_headers())
    response.raise_for_status()
    
    return response.json().get("sectors", []) if response.status_code == 200 else []

def fetch_sector_insights():
    """Fetch available sectors from API."""
    response = requests.get(f"{API_BASE_URL}/insights", headers=get_headers())
    response.raise_for_status()
    
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
    response = requests.get(f"{API_BASE_URL}/companies", params=params, headers=get_headers())
    response.raise_for_status()
    
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
    response = requests.get(f"{API_BASE_URL}/sensor-data", params=params, headers=get_headers())
    response.raise_for_status()

    print(response.json())
    
    if response.status_code == 200:
        return pd.DataFrame(response.json().get("sensor_data", []))
    return pd.DataFrame()

def register_user(username: str, password: str, confirm_password: str):
    """Register a new user."""
    if not password or len(password) < 1:
        st.toast("Password cannot be empty.", icon="❌")
        st.stop()
    if password != confirm_password:
        st.toast("Passwords do not match.", icon="❌")
        st.stop()

    try:
        response = requests.post(f"{API_BASE_URL}/register", json={"username": username, "password": password})
        response.raise_for_status()

        return response.status_code == 201
    except requests.RequestException as e:
        st.toast("Registration failed. Try again.", icon="❌")
        st.toast(f"Error: {e}", icon="❌")

class User(BaseModel):
    username: str
    token: str

def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Send login request to API
    
    Args:
        username (str): Username
        password (str): Password
    
    Returns:
        User: User object with username and token if login is successful
        None: If login fails
    
    Raises:
        requests.RequestException: If an error occurs during the request
    """

    API_URL = f"{API_BASE_URL}/login"
    payload = {"username": username, "password": password}

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()

        data = response.json()
        if "token" in data.keys():
            return User(username=username, token=data["token"])
    except requests.RequestException as e:
        print(f"Error authenticating user: {e}")
        pass
    return None
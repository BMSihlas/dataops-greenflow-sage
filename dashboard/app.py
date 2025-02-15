import streamlit as st
import pandas as pd
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://greenflow_api:8000")

st.set_page_config(page_title="GreenFlow Sage - Dashboard", layout="wide")

st.title("📊 GreenFlow Sage Dashboard")
st.write("Monitoring energy, water, and CO2 emissions.")

@st.cache_data(ttl=300)
def fetch_data():
    response = requests.get(f"{API_BASE_URL}/insights")
    if response.status_code == 200:
        data = response.json().get("insights", [])
        return pd.DataFrame(data)
    else:
        st.error("Failed to fetch data from API.")
        return pd.DataFrame()

df = fetch_data()

if not df.empty:
    st.dataframe(df)

    df.set_index("sector", inplace=True)

    st.subheader("Average Energy Consumption (kWh) by Sector")
    st.bar_chart(df["avg_energy_kwh"])

    st.subheader("Average Water Consumption (m³) by Sector")
    st.bar_chart(df["avg_water_m3"])

    st.subheader("Average CO2 Emissions by Sector")
    st.bar_chart(df["avg_co2_emissions"])

else:
    st.warning("No data available.")


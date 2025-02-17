import streamlit as st
from components.api_utils import fetch_sectors, fetch_companies_by_sector

def sector_selector():
    """Dropdown for sector selection."""
    sectors = fetch_sectors()
    return st.selectbox("Select Sector", ["All"] + sectors)

def order_by_selector():
    """Dropdown for sector selection."""
    col1, col2 = st.columns([1.2, 0.7])
    with col1:
        order_by = st.selectbox("Order by", ["nr.", "energy_kwh", "water_m3", "co2_emissions"])
    with col2:
        order_dir = st.selectbox("Order", ["asc", "desc"])
    return order_by, order_dir

def company_selector(selected_sector):
    """Dropdown for company selection with pagination."""
    current_page = st.number_input("Page", min_value=1, step=1, value=1)
    companies, total_pages = fetch_companies_by_sector(selected_sector, current_page)
    
    # Display pagination info
    st.write(f"Page {current_page} of {total_pages}")
    
    return st.selectbox("Select Company", ["All"] + companies)

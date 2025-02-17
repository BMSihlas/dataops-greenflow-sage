import os
import streamlit as st
import pandas as pd
from components.api_utils import fetch_companies_by_sector
from components.visualizations import plot_bar_chart
from components.ui_components import sector_selector, order_by_selector
import time

def sector():

    st.header("🔍 Sector-Specific Analysis")
    st.write("Explore company-level details within a selected sector.")

    time.sleep(0.3)

    selected_sector = sector_selector()

    st.subheader(f"Companies in Sector {selected_sector}")

    col1, col2, col3 = st.columns([1, 0.5, 0.5])
    with col1:
        order_by, order_dir = order_by_selector()
    with col2:
        page_size = st.selectbox("Results per Page", [5, 10, 15, 20], index=1)
    with col3:
        page = st.number_input("Current Page", min_value=1, value=1, step=1)

    company_data, total_pages = fetch_companies_by_sector(selected_sector, page_size=page_size)

    if total_pages < 1:
        st.warning(f"No company data available for {selected_sector}.")
        st.stop()

    if page > total_pages:
        st.warning(f"Only {total_pages} pages available.")
        page = total_pages

    company_data, total_pages = fetch_companies_by_sector(selected_sector, page=page, page_size=page_size, order_by=order_by, order_dir=order_dir)

    if not company_data:
        st.warning(f"No company data available for {selected_sector}.")
    else:
        company_df = pd.DataFrame(company_data)

        st.dataframe(company_df)
        st.write(f"Page {page} of {total_pages}")
        
        # Charts for company-specific insights
        st.subheader(f"Energy, Water, and CO₂ Insights for {selected_sector}")
        col1, col2 = st.columns(2)
        with col1:
            plot_bar_chart(company_df, x="company", y="energy_kwh", ylabel="Energy (kWh)", title="Energy Consumption (kWh)")
        with col2:
            ""
            
        col1, col2 = st.columns(2)
        with col1:
            plot_bar_chart(company_df, x="company", y="water_m3", ylabel="Water (m³)", title="Water Usage (m³)")
        with col2:
            ""
            
        col1, col2 = st.columns(2)
        with col1:
            plot_bar_chart(company_df, x="company", y="co2_emissions", ylabel="CO₂ Emissions", title="CO₂ Emissions")
        with col2:
            ""
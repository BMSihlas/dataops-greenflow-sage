import os
import streamlit as st
import pandas as pd
from components.api_utils import fetch_sector_insights, fetch_companies_by_sector
from components.visualizations import plot_bar_chart, plot_correlation_heatmap
from components.ui_components import sector_selector, order_by_selector

def dashboard():

    st.header("📊 Global Sector Overview")
    st.subheader("📊 Sector-Wide Environmental Averages")
    st.write("This section provides a high-level summary of energy, water, and CO₂ emissions by sector.")

    # Load sector insights
    sector_data = fetch_sector_insights()
    if sector_data is None:
        st.error("Failed to fetch sector insights. Check API connection.")
        st.stop()

    sector_df = pd.DataFrame(sector_data)

    tab1, tab2, tab3, tab4 = st.tabs(["Energy Consumption", "Water Usage", "CO₂ Emissions", "Correlation Heatmap"])

    with tab1:
        col1, col2 = st.columns(2)
        # Display sector-wide averages
        with col1:
            st.subheader("Average Energy Consumption by Sector")
            plot_bar_chart(sector_df, x="sector", y="avg_energy_kwh", ylabel="Avg Energy (kWh)")
        with col2:
            ""

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Average Water Usage by Sector")
            plot_bar_chart(sector_df, x="sector", y="avg_water_m3", ylabel="Avg Water (m³)")
        with col2:
            ""

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Average CO₂ Emissions by Sector")
            plot_bar_chart(sector_df, x="sector", y="avg_co2_emissions", ylabel="Avg CO₂ Emissions")
            ""
    
    with tab4:
        # Heatmap
        st.subheader("Correlation Heatmap of Environmental Factors")
        numeric_sector_df = sector_df.select_dtypes(include=['number'])
        plot_correlation_heatmap(numeric_sector_df)
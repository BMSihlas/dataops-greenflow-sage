import os
import streamlit as st
import pandas as pd
from api_utils import fetch_sector_insights, fetch_companies_by_sector
from visualizations import plot_bar_chart, plot_correlation_heatmap
from ui_components import sector_selector, order_by_selector

st.set_page_config(page_title="GreenFlow Sage - Dashboard", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "General Overview"

st.title("📊 GreenFlow Sage")
st.subheader("Welcome")

# Sidebar - Navigation
image_path = os.path.join("dashboard", "assets", "greenflow_logo.png")
st.sidebar.image(image_path, width=120, use_container_width=True)
st.sidebar.subheader("Navigation")

# Clickable buttons to change page
if st.sidebar.button(label="📊 Overview", use_container_width=True):
    st.session_state.page = "General Overview"
if st.sidebar.button(label="🔍 Detailed View", use_container_width=True):
    st.session_state.page = "Detailed Sector View"

st.sidebar.markdown("---")
st.sidebar.subheader("📌 About the Author")
st.sidebar.markdown(
    """
    **Bruno Matos**  
    Fullstack Developer & Software Engineer  
    Passionate about Programming, Data, and Sustainable Tech.  
    [🔗 GitHub](https://github.com/BMSihlas) | [📧 Contact](mailto:bruno.rosal.matos@gmail.com)
    """
)

# Load sector insights
sector_data = fetch_sector_insights()
if sector_data is None:
    st.error("Failed to fetch sector insights. Check API connection.")
    st.stop()

sector_df = pd.DataFrame(sector_data)

# General Overview Tab
if st.session_state.page == "General Overview":
    st.header("📊 General Sector Overview")
    st.subheader("📊 Sector-Wide Environmental Averages")
    st.write("This section provides a high-level summary of energy, water, and CO₂ emissions by sector.")
    col1, col2 = st.columns(2)

    # Display sector-wide averages
    with col1:
        st.subheader("Average Energy Consumption by Sector")
        plot_bar_chart(sector_df, x="sector", y="avg_energy_kwh", ylabel="Avg Energy (kWh)")
    with col2:
        ""

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average Water Usage by Sector")
        plot_bar_chart(sector_df, x="sector", y="avg_water_m3", ylabel="Avg Water (m³)")
    with col2:
        ""

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average CO₂ Emissions by Sector")
        plot_bar_chart(sector_df, x="sector", y="avg_co2_emissions", ylabel="Avg CO₂ Emissions")
        ""
    
    # Heatmap
    st.subheader("Correlation Heatmap of Environmental Factors")
    numeric_sector_df = sector_df.select_dtypes(include=['number'])
    plot_correlation_heatmap(numeric_sector_df)

# Detailed Sector View Tab
elif st.session_state.page == "Detailed Sector View":
    st.header("🔍 Sector-Specific Analysis")
    st.write("Explore company-level details within a selected sector.")

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
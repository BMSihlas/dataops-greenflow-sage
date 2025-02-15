import sys
from .utils import load_env, get_db_engine, fetch_table_data, insert_data_into_db
import pandas as pd

# Constants
TABLE_SENSOR_DATA: str = "sensor_data"
TABLE_INSIGHTS: str = "insights"

def compute_insights(df: pd.DataFrame) -> pd.DataFrame:
    """Computes sector-wise sustainability insights."""
    if df.empty:
        print("Warning: No data found in sensor_data table. Insights table will not be updated.")
        return pd.DataFrame()

    insights_df: pd.DataFrame = df.groupby("sector").agg({
        "energy_kwh": "mean",
        "water_m3": "mean",
        "co2_emissions": "mean"
    }).reset_index()

    # Rename columns to match PostgreSQL schema
    insights_df.rename(columns={
        "energy_kwh": "avg_energy_kwh",
        "water_m3": "avg_water_m3",
        "co2_emissions": "avg_co2_emissions"
    }, inplace=True)

    return insights_df

def main() -> bool:
    """Main function to orchestrate insights processing."""
    try:
        print("Starting insights computation process...")
        load_env()  # Load & validate environment variables
        engine = get_db_engine()  # Create DB connection
        df = fetch_table_data(engine, TABLE_SENSOR_DATA)  # Fetch data

        if df is not None:
            insights_df = compute_insights(df)  # Compute insights
            if not insights_df.empty:
                return insert_data_into_db(engine, insights_df, TABLE_INSIGHTS)  # Insert into DB
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

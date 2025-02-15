import os
import sys
from .utils import load_env, get_db_engine, load_parquet_data, insert_data_into_db

# Constants
PARQUET_FILE_PATH: str = "data/dados_sensores_5000.parquet"
TABLE_NAME: str = "sensor_data"
COLUMN_MAPPING: dict[str, str] = {
    "empresa": "company",
    "energia_kwh": "energy_kwh",
    "agua_m3": "water_m3",
    "co2_emissoes": "co2_emissions",
    "setor": "sector"
}

def main() -> bool:
    """Main function to orchestrate data loading."""
    try:
        print("Starting data loading process...")
        load_env()  # Load & validate environment variables
        engine = get_db_engine()  # Create DB connection
        if engine is None:
            raise ConnectionError("Error: Database connection not established.")
        
        if not os.path.exists(PARQUET_FILE_PATH):
            raise FileNotFoundError(f"Error: Parquet file not found at {PARQUET_FILE_PATH}")

        df = load_parquet_data(PARQUET_FILE_PATH, COLUMN_MAPPING)  # Load Parquet data
        return insert_data_into_db(engine, df, TABLE_NAME)  # Insert into DB
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

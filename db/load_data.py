import os
import sys
from .utils import load_env, get_db_engine, load_parquet_data, insert_data_into_db

# Constants
PARQUET_FILE_PATH: str = "data/dados_sensores_5000.parquet"
DATA_DIR: str = "data"
TABLE_NAME: str = "sensor_data"
COLUMN_MAPPING: dict[str, str] = {
    "empresa": "company",
    "energia_kwh": "energy_kwh",
    "agua_m3": "water_m3",
    "co2_emissoes": "co2_emissions",
    "setor": "sector"
}

def main(path_to_file: str = "") -> bool:
    """Main function to orchestrate data loading."""
    try:
        print("Starting data loading process...")
        load_env()  # Load & validate environment variables
        engine = get_db_engine()  # Create DB connection
        if engine is None:
            raise ConnectionError("Error: Database connection not established.")
        
        final_path_to_file = ""
        if len(path_to_file) > 0 and not os.path.exists(f"{DATA_DIR}/{path_to_file}"):
            raise FileNotFoundError(f"Error: Parquet file not found at {DATA_DIR}/{path_to_file}")
        elif len(path_to_file) > 0 and os.path.exists(f"{DATA_DIR}/{path_to_file}"):
            final_path_to_file = f"{DATA_DIR}/{path_to_file}"
        elif not os.path.exists(PARQUET_FILE_PATH):
            raise FileNotFoundError(f"Error: Parquet file not found at {PARQUET_FILE_PATH}")
        else:
            final_path_to_file = PARQUET_FILE_PATH

        df = load_parquet_data(final_path_to_file, COLUMN_MAPPING)  # Load Parquet data
        return insert_data_into_db(engine, df, TABLE_NAME)  # Insert into DB
    except Exception as e:
        print(f"Error occurred: {e}")
        raise e

if __name__ == "__main__":
    main()

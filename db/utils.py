import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from dotenv import load_dotenv, find_dotenv
from typing import Dict, Optional

ENV_VARS: list[str] = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_HOST", "POSTGRES_PORT"]

def load_env() -> None:
    """Loads environment variables and validates required ones."""
    if not find_dotenv():
        print("Warning: .env file not found. Ensure it exists before running this script.")
    
    load_dotenv()

    # Validate required environment variables
    missing_vars: list[str] = [var for var in ENV_VARS if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

def get_db_engine() -> Engine:
    """Creates and returns a PostgreSQL SQLAlchemy engine."""
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "")

    if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB]):
        print("Error: One or more required database environment variables are missing.")
        sys.exit(1)

    database_url: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    return create_engine(database_url)

def load_parquet_data(file_path: str, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Loads Parquet data into a Pandas DataFrame.
    
    Args:
        file_path (str): Path to the Parquet file.
        column_mapping (Dict[str, str]): Mapping of original column names to PostgreSQL column names.
    
    Returns:
        pd.DataFrame: Transformed DataFrame with renamed columns.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Parquet file not found at {file_path}")

    print(f"Reading Parquet file: {file_path}")
    df: pd.DataFrame = pd.read_parquet(file_path)

    # Rename columns to match PostgreSQL schema
    df.rename(columns=column_mapping, inplace=True)

    return df

def insert_data_into_db(engine: Engine, df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> bool:
    """
    Inserts DataFrame data into a PostgreSQL table.
    
    Args:
        engine (Engine): Database engine connection.
        df (pd.DataFrame): DataFrame containing data to insert.
        table_name (str): Name of the target table.
        if_exists (str): How to handle existing data ("replace", "append", "fail").
    """
    print(f"Inserting data into PostgreSQL table: {table_name}...")
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    print(f"Data successfully loaded into {table_name}.")
    return True

def fetch_table_data(engine: Engine, table_name: str) -> Optional[pd.DataFrame]:
    """
    Fetches all data from a given PostgreSQL table.
    
    Args:
        engine (Engine): Database engine connection.
        table_name (str): Name of the table.
    
    Returns:
        Optional[pd.DataFrame]: Data from the table or None if empty.
    """
    query: str = f"SELECT * FROM {table_name}"
    df: pd.DataFrame = pd.read_sql(query, engine)

    if df.empty:
        print(f"Warning: No data found in {table_name} table.")
        return None

    return df

def main() -> None:
    #
    None
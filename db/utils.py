import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Engine
from dotenv import load_dotenv, find_dotenv
from typing import Dict, Optional
import bcrypt
from pydantic import BaseModel
import time

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

def fetch_table_data(engine: Engine, table_name: str, where: str = "") -> Optional[pd.DataFrame]:
    """
    Fetches all data from a given PostgreSQL table.
    
    Args:
        engine (Engine): Database engine connection.
        table_name (str): Name of the table.
    
    Returns:
        Optional[pd.DataFrame]: Data from the table or None if empty.
    """
    query: str = f"SELECT * FROM {table_name}"
    if where and len(where) > 0:
        query += f" WHERE {where}"
    df: pd.DataFrame = pd.read_sql(query, engine)

    if df.empty:
        print(f"Warning: No data found in {table_name} table.")
        return None

    return df

def register_user(username: str, password: str) -> bool:
    """
    Register a new user with a hashed password and salt.

    Args:
        username (str): User's username.
        password (str): User's password.
    Returns:
        bool: True if user was successfully registered, False otherwise.
    Raises:
        ValueError: If username or password are empty or too short.
    """
    if not username or not password:
        raise ValueError("Username and password are required fields.")
    
    if len(username) < 4:
        raise ValueError("Username must be at least 4 characters long.")
    
    if len(password) < 4:
        raise ValueError("Password must be at least 4 characters long.")

    try:
        salt = bcrypt.gensalt()

        password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)

        user_data = {
            "username": username,
            "password_hash": password_hash.decode("utf-8"),
            "created_at": int(time.time())
        }

        df = pd.DataFrame([user_data], columns=user_data.keys())

        engine = get_db_engine()
        return insert_data_into_db(engine, df, "users", if_exists="append")
    except Exception as e:
        if "duplicate key value violates unique constraint" in str(e).lower():
            raise ValueError("Error registering user: Username already exists.")
        raise ValueError(f"Error registering user: {str(e)}")

class User(BaseModel):
    username: str
    password_hash: str

def find_user(username: str) -> User:
    """
    Fetchs an existing user and return their data.
    
    Args:
        username (str): User's username.
    
    Returns:
        User: User data (username, password hash, salt).
    """
    engine = get_db_engine()
    df = fetch_table_data(engine, "users", f"username = '{username}' LIMIT 1 OFFSET 0")

    if df is None:
        raise ValueError("Invalid credentials: User not found")

    user_data = df.iloc[0].to_dict()
    return User(**user_data)

def login_user(username: str, password: str) -> bool:
    """
    Login an existing user with a given username and password.
    
    Args:
        username (str): User's username.
        password (str): User's password.
    
    Returns:
        bool: True if login was successful.
    Raises:
        ValueError: If username or password are invalid.
    """
    user = find_user(username)
    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise ValueError("Invalid credentials: Password does not match")
    
    try:
        sql = text("UPDATE users SET last_login = :last_login WHERE username = :username")
        engine = get_db_engine()
        with engine.connect() as conn:
            conn.execute(sql, {"last_login": int(time.time()), "username": username})
            conn.commit()
        return True
    except Exception as e:
        raise ValueError(f"Error logging in user: {str(e)}")

def main() -> None:
    #
    None

if __name__ == "__main__":
    main()
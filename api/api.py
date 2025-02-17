import os
import sys
from fastapi import FastAPI, HTTPException, Depends, Header, APIRouter, Query, Security, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.engine.base import Engine
from dotenv import load_dotenv, find_dotenv
from db.utils import get_db_engine, fetch_table_data, register_user, login_user
from db.load_data import main as deploy_parquet_data
from db.process_insights import main as process_insights
from typing import Optional
from pydantic import BaseModel, ValidationError
import jwt
import datetime
from pathlib import Path
import pandas as pd

ENV_VARS: list[str] = ["API_SECRET_KEY", "API_AUTH_SECRET_KEY"]

"""Loads environment variables and validates required ones."""
if not find_dotenv():
    print("Warning: .env file not found. Ensure it exists before running this script.")

load_dotenv()

# Validate required environment variables
missing_vars: list[str] = [var for var in ENV_VARS if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# Retrieve API Key from environment variables
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
API_AUTH_SECRET_KEY = os.getenv("API_AUTH_SECRET_KEY")
ALGORITHM: str = "HS256"
TTL = 24 * 60  # 24 hours
DATA_DIR = Path("/app/data")

# Initialize FastAPI app
app = FastAPI(
    title="GreenFlow Sage API",
    description="API to serve sustainability insights from sensor data",
    version="1.0"
)

router = APIRouter(prefix="/api/v1")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def db_connect() -> Engine:
    return get_db_engine()

def create_jwt_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=TTL)
    }
    return jwt.encode(payload, API_AUTH_SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Security(oauth2_scheme)):
    """Validate JWT token and return the username."""
    try:
        payload = jwt.decode(token, API_AUTH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/")
def root():
    """Root endpoint to check API health."""
    return {"message": "GreenFlow Sage API is running!"}

@router.get("/insights")
def get_insights(username: str = Depends(get_current_user)):
    """Fetch sustainability insights from PostgreSQL."""
    try:
        engine = db_connect()

        insights_df = fetch_table_data(engine, "insights")
        if insights_df is None or insights_df.empty:
            raise HTTPException(status_code=404, detail="No insights found.")
        
        insights = insights_df.to_dict(orient="records")
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching insights: {str(e)}")

@router.get("/insights/{sector}")
def get_sector_insights(sector: str, username: str = Depends(get_current_user)):
    """Fetch insights for a specific sector."""
    try:
        engine = db_connect()

        insights_df = fetch_table_data(engine, "insights")
        insights_df = insights_df[insights_df["sector"] == sector]

        if insights_df.empty:
            raise HTTPException(status_code=404, detail=f"No insights found for sector: {sector}")
        
        insights = insights_df.to_dict(orient="records")
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching insights for {sector}: {str(e)}")

@router.get("/sectors")
def get_sectors(username: str = Depends(get_current_user)):
    """Fetch list of unique sectors from PostgreSQL."""
    try:
        engine = db_connect()

        insights_df = fetch_table_data(engine, "insights")
        sectors = insights_df["sector"].unique().tolist()

        return {"sectors": sectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sectors: {str(e)}")

@router.get("/sensor-data")
def get_sensor_data(limit: int = 10, username: str = Depends(get_current_user)):
    """Fetch latest sensor data records from PostgreSQL."""
    try:
        engine = db_connect()

        sensor_data_df = fetch_table_data(engine, "sensor_data")

        if sensor_data_df is None or sensor_data_df.empty:
            raise HTTPException(status_code=404, detail="No sensor data found.")
        
        sensor_data = sensor_data_df.to_dict(orient="records")
        return {"sensor_data": sensor_data[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sensor data: {str(e)}")

class LoadDataRequest(BaseModel):
    filename: Optional[str] = None

@router.post("/load-data")
def load_data(
    request: LoadDataRequest,
    x_api_key: str = Header(None),
    username: str = Depends(get_current_user)
):
    """Secure API to load Parquet data into PostgreSQL."""
    if not x_api_key or x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")
    
    filename = request.filename.strip() if request.filename else None
    if filename is not None and filename != "":
        if not filename.endswith(".parquet"):
            raise HTTPException(status_code=400, detail="File must be a Parquet file (.parquet)")

    try:
        load_success = deploy_parquet_data(filename if filename is not None else "")

        if filename is not None and filename != "":
            file = DATA_DIR / filename
            if file.exists():
                print(f"Attempting to delete: {file}")  # Debugging
                if os.access(file, os.W_OK):  # Check if write access is allowed
                    file.unlink(missing_ok=True)
                    print(f"File deleted: {file}")  # Debugging
                else:
                    print(f"File not writable: {file}")  # Debugging
                    raise HTTPException(status_code=403, detail="File cannot be deleted due to insufficient permissions.")
            else:
                print(f"File does not exist: {file}")
        else:
            print("No filename provided.")

        if load_success:
            if not process_insights():
                return {"message": "Failed to load processed insights into PostgreSQL."}
            else:
                return {"message": "Data successfully loaded into PostgreSQL."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@router.get("/companies")
def get_companies(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    page: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Number of results per page"),
    order_by: Optional[str] = Query("nr", description="Order by column"),
    order_dir: Optional[str] = Query(None, description="Order direction (asc or desc)"),
    username: str = Depends(get_current_user)
):
    """Fetch paginated list of companies from PostgreSQL."""
    try:
        engine = db_connect()
        company_df = fetch_table_data(engine, "sensor_data")

        if company_df is None or company_df.empty:
            raise HTTPException(status_code=404, detail="No companies found.")
        
        required_columns = {"company", "sector", "energy_kwh", "water_m3", "co2_emissions"}
        if not required_columns.issubset(company_df.columns):
            raise HTTPException(status_code=500, detail="Missing required columns in database table.")
        
        if sector:
            company_df = company_df[company_df["sector"] == sector]
        
        company_df = company_df.reset_index(drop=True)
        company_df.insert(0, "nr.", company_df.index + 1)

        if order_by and order_by in company_df.columns:
            ascending = order_dir.lower() != "desc"
            company_df = company_df.sort_values(by=order_by, ascending=ascending)

        total_pages = max((len(company_df) + page_size - 1) // page_size, 1)
        page = max(1, min(page, total_pages))
        paginated_companies = company_df.iloc[(page - 1) * page_size : page * page_size]

        companies_list = paginated_companies.to_dict(orient="records")

        return {
            "companies": companies_list,
            "total_pages": total_pages,
            "current_page": page
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching companies: {str(e)}")

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    """Login an existing user."""

    try:
        login_user(request.username, request.password)

        token = create_jwt_token(request.username)

        return {
            "message": "Login successful!",
            "token": token
        }

    except ValueError as e:
        print("Error logging in user:", str(e))
        raise HTTPException(status_code=400, detail="Invalid credentials")

class RegisterRequest(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    """Register a new user."""
    try:
        if not register_user(request.username, request.password):
            raise HTTPException(status_code=400, detail="Error registering user")

        return {
            "message": "User registered successfully!",
        }
    except ValueError as e:
        print("Error registering user:", str(e))
        raise HTTPException(status_code=400, detail="Error registering user")

class ParquetFileLoadDataSchema(BaseModel):
    """Define expected Parquet file structure."""
    empresa: str
    energia_kwh: float
    agua_m3: float
    co2_emissoes: float
    setor: str

def validate_parquet(file_path: Path) -> pd.DataFrame:
    """Validate Parquet file structure using Pydantic."""
    try:
        df = pd.read_parquet(file_path)

        # Ensure required columns exist
        required_columns = ParquetFileLoadDataSchema.__annotations__.keys()
        missing_columns = set(required_columns) - set(df.columns)

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Validate each row using Pydantic
        for _, row in df.iterrows():
            ParquetFileLoadDataSchema(**row.to_dict())

        return df

    except ValidationError as e:
        raise ValueError(f"Data validation error: {e}")

    except Exception as e:
        raise ValueError(f"Invalid Parquet format: {str(e)}")

@router.post("/upload-parquet", status_code=status.HTTP_201_CREATED)
async def upload_parquet(
    x_api_key: str = Header(None),
    file: UploadFile = File(...),
    username: str = Depends(get_current_user)
):
    """Secure API to load Parquet data into PostgreSQL."""
    if not x_api_key or x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")
    
    """Upload and validate a Parquet file using Pydantic, then store it in /data."""
    if not file.filename.endswith(".parquet"):
        raise HTTPException(status_code=400, detail="File must be a Parquet file (.parquet)")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIR / file.filename
    temp_file_path = DATA_DIR / f"temp_{file.filename}"

    if file_path.exists():
        raise HTTPException(status_code=400, detail="File already exists. Choose a different name.")

    try:
        # Save the file temporarily
        with temp_file_path.open("wb") as f:
            f.write(file.file.read())

        # Validate the file structure
        validate_parquet(temp_file_path)

        # Rename temp file to final filename only if validation succeeds
        temp_file_path.rename(file_path)

        return {"message": "File uploaded and validated successfully", "filename": file.filename}

    except ValueError as e:
        # Remove invalid file
        temp_file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(e))

app.include_router(router)

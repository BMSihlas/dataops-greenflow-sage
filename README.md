# GreenFlow-Sage

A sustainability insights project that processes sensor data, stores it in PostgreSQL, and exposes insights via an API and an interactive dashboard.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Contributing](#contributing)
8. [Contact](#contact)

## 1. Project Overview

GreenFlow-Sage is designed to provide actionable sustainability insights by processing sensor data. The system ingests raw data, processes and stores it in a PostgreSQL database, and offers access to these insights through a FastAPI-based API and a Streamlit-powered interactive dashboard.

A working mockup of the project is deployed on Render.com:
- You can access the dashboard at [https://greenflow-sage-dashboard.onrender.com](https://greenflow-sage-dashboard.onrender.com).
- You can look into the API documentation at [https://greenflow-sage-api.onrender.com/docs](https://greenflow-sage-api.onrender.com/docs).
   - for the requesting the API secret key, please contact the project maintainers.

## 2. Features

- **Data Ingestion**: Handles raw sensor data in Parquet format.
- **Data Processing**: Transforms and stores data in PostgreSQL for efficient querying.
- **API Access**: FastAPI backend providing endpoints to retrieve processed insights.
- **Interactive Dashboard**: Streamlit dashboard for visualizing data trends and insights.

### 2.1 - Detailed Features

- Containerized Development Environment: Runs on Docker with separate containers for:
   - greenflow_db: PostgreSQL database
   - greenflow_api: REST server using FastAPI, SQLAlchemy, and Pydantic
   - greenflow_dashboard: Streamlit dashboard consuming the API

- Data Ingestion:
   - Upload Parquet files through the API
   - Load previously uploaded Parquet files into the database
- User Authentication:
   - User registration and login with JWT token authentication (24-hour expiration)
   - Protected API endpoints requiring valid JWT tokens
- Interactive Dashboard:
   - User authentication integrated with API
   - Insights available upon successful login
   - JWT token and username persisted in local storage while valid
   - Logical grouping of insights across multiple pages
   - Integrated navigation menu
- Production Deployment:
   - Replicated production environment on Render.com
   - Includes PostgreSQL database, API service, and dashboard service

## 3. Project Structure

```plaintext
root/
│   api/
│   ├── # FastAPI backend
│   ├── api.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   
│   dashboard/
│   ├── # Streamlit dashboard
│   ├── account/
│   ├── assets/
│   ├── components/
│   ├── extra/
│   ├── reports/
│   ├── tools/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   
│   data/
│   ├── # Raw sensor data files
│   
│   db/
│   ├── # PostgreSQL setup and data initialization
│   ├── __init__.py
│   ├── load_data.py
│   ├── process_insights.py
│   ├── schema.sql
│   ├── utils.py
│   
│   notebooks/
│   ├── # Python notebooks for data exploration
|   ├── Sensors_raw_data_insights.ipynb
│   
│   .dockerignore
│   .gitignore
│   docker-compose.yaml
│   README.md
```

- `api/`: FastAPI backend to serve insights.
- `dashboard/`: Streamlit dashboard for visualization.
- `db/`: PostgreSQL setup and data initialization scripts.
- `data/`: Directory for raw sensor data files.
- `notebooks/`: Python notebooks for data exploration.
- `docker-compose.yaml`: Orchestrates the multi-container Docker application.

## 4. Installation

To set up the project locally:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/BMSihlas/dataops-greenflow-sage.git
   cd dataops-greenflow-sage
   ```

2. **Set up environment variables**:

    This tool uses `.env` files to store the environment variables. Create a copy of the `.env.example` file and rename it to `.env`. Fill in the required values.

3. **Build and start the services**:

   Ensure you have Docker and Docker Compose installed. Then, run:

   ```bash
   docker-compose up --build
   ```

   This command will build and start the PostgreSQL database, FastAPI backend, and Streamlit dashboard.

## 5. Usage

Once the services are running:

- **API**: Access the FastAPI documentation at `http://localhost:8000/docs`. Here, you can explore the available endpoints.

- **Dashboard**: View the interactive dashboard at `http://localhost:8501`. This dashboard visualizes the processed data and provides insights.

- **Notebooks**: You can explore the sensor raw data insights using the Python notebook `notebooks/Sensors_raw_data_insights.ipynb`.

### 5.1 Using the API

#### 5.1.1 Endpoints
For the complete API Documentation:
> Access at http://localhost:8000/docs.

- GET `/api/v1/insights`: Retrieve all insights.
- GET `/api/v1/insights/{sector_name}`: Retrieve insights from a specific sector.
- GET `/api/v1/sectors`: Retrieve a list with all sectors.
   - e.g. `/api/v1/insights/Varejo`
- GET `/api/v1/companies`: Retrieve a list with all companies.
   - Query Parameters:
      - `page`: Page number for pagination. [default: 1]
      - `page_size`: Number of items per page. [default: 10]
      - `sector`: Filter by sector name.
      - `order_by`: Field to order by. [default: energy_kwh]
      - `order_dir`: Order direction. [asc, desc]
   - e.g. `/api/v1/companies?page=1&page_size=10&sector=Saúde&order_by=energy_kwh&order_dir=desc`
- POST `/api/v1/register`: Register a new user.
   - Request Body: `{"username": "user", "password": "password"}`
- POST `/api/v1/login`: Authenticate and receive a JWT token.
   - Request Body: `{"username": "user", "password": "password"}`
- POST `/api/v1/upload-parquet`: Upload a Parquet file.
   - Header: `x-api-key: <API secret key>`
   - Authorization Header: `Authorization: Bearer <JWT token>`
   - Form-Data: `file: <Parquet file>`
- POST `/api/v1/load-data`: Load the uploaded data into PostgreSQL.
   - Header: `x-api-key: <API secret key>`
   - Authorization Header: `Authorization: Bearer <JWT token>`
   - Request Body: `{"filename": "filename_of_the_uploaded_file.parquet"}`

#### 5.1.2 Steps to load sensor data into database and process insights

1. Register a User:
   - Call the `POST /api/v1/register` endpoint with a username and password.

2. Authenticate:
   - Call `POST /api/v1/login` with credentials to receive a JWT token.

3. Upload a Parquet File:
   - Call `POST /api/v1/upload-parquet` with the Parquet file to upload.

4. Load the Uploaded Data into PostgreSQL:
   - Call `POST /api/v1/load-data` with the filename of the uploaded file.

5. Access Processed Insights:
   - After loading the data, the insights can be accessed via the dashboard or API endpoints.

### 5.2 Using the Dashboard
- Dashboard: View the interactive dashboard at http://localhost:8501.

## 6. Contributing

We welcome contributions to enhance GreenFlow-Sage. To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your_feature_name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/your_feature_name`.
5. Open a pull request detailing your changes.

Please ensure your code adheres to the project's coding standards and includes relevant tests.

## 7. Contact

For questions or suggestions, please open an issue in this repository or contact the project maintainers directly.


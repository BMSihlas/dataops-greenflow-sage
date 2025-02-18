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

## Project Overview

GreenFlow-Sage is designed to provide actionable sustainability insights by processing sensor data. The system ingests raw data, processes and stores it in a PostgreSQL database, and offers access to these insights through a FastAPI-based API and a Streamlit-powered interactive dashboard.

## Features

- **Data Ingestion**: Handles raw sensor data in Parquet format.
- **Data Processing**: Transforms and stores data in PostgreSQL for efficient querying.
- **API Access**: FastAPI backend providing endpoints to retrieve processed insights.
- **Interactive Dashboard**: Streamlit dashboard for visualizing data trends and insights.

## Project Structure

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

## Installation

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

## Usage

Once the services are running:

- **API**: Access the FastAPI documentation at `http://localhost:8000/docs`. Here, you can explore the available endpoints.

- **Dashboard**: View the interactive dashboard at `http://localhost:8501`. This dashboard visualizes the processed data and provides insights.

- **Notebooks**: You can explore the sensor raw data insights using the Python notebook `notebooks/Sensors_raw_data_insights.ipynb`.

## Contributing

We welcome contributions to enhance GreenFlow-Sage. To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your_feature_name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/your_feature_name`.
5. Open a pull request detailing your changes.

Please ensure your code adheres to the project's coding standards and includes relevant tests.

## Contact

For questions or suggestions, please open an issue in this repository or contact the project maintainers directly.


# GreenFlow-Sage

A sustainability insights project that processes sensor data, stores it in PostgreSQL, and exposes insights via an API and an interactive dashboard.

## Project Structure
- **api/** → FastAPI backend to serve insights
- **dashboard/** → Streamlit dashboard for visualization
- **data/** → Parquet file containing raw sensor data
- **db/** → PostgreSQL setup & insight processing scripts
- **scripts/** → Automation scripts (e.g., update insights)
- **docker-compose.yml** → Orchestrates API, Dashboard, and PostgreSQL

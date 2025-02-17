FROM python:3.10.11

WORKDIR /app

RUN pip install --upgrade pip

COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard /app/dashboard

RUN mkdir -p ~/.streamlit && echo "[browser]" > ~/.streamlit/config.toml && echo "gatherUsageStats = false" >> ~/.streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave", "true", "--server.enableCORS", "true"]

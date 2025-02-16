FROM python:3.10.11

WORKDIR /app

COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard /app/dashboard

RUN mkdir -p ~/.streamlit && echo "[browser]" > ~/.streamlit/config.toml && echo "gatherUsageStats = false" >> ~/.streamlit/config.toml

EXPOSE ${DASHBOARD_PORT}

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=${DASHBOARD_PORT}", "--server.address=0.0.0.0"]

FROM python:3.10.11

WORKDIR /app

RUN pip install --upgrade pip

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./db /app/db

COPY ./api /app/api
# RUN ls -la /app/api/entrypoint.sh && chmod +x /app/api/entrypoint.sh

ENV PYTHONPATH=/app

# CMD ["/bin/sh", "-c", "/app/api/entrypoint.sh"]
CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "${API_PORT}"]


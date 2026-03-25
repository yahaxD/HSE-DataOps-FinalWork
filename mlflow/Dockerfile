FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir mlflow psycopg2-binary

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "postgresql://${MLFLOW_DB_USER}:${MLFLOW_DB_PASSWORD}@postgres:5432/${MLFLOW_DB_NAME}", \
     "--default-artifact-root", "/mlflow/artifacts"]

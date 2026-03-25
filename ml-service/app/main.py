import time
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, text
from sqlalchemy.orm import declarative_base, Session
import os
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log_record, ensure_ascii=False)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("inference_service")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

REQUEST_COUNT   = Counter("ml_requests_total",         "Total prediction requests")
REQUEST_ERRORS  = Counter("ml_request_errors_total",   "Total prediction errors")
REQUEST_LATENCY = Histogram("ml_request_latency_seconds", "Prediction latency in seconds")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./predictions.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "predictions"
    id            = Column(Integer, primary_key=True, index=True)
    timestamp     = Column(DateTime, default=datetime.utcnow)
    input_data    = Column(String)
    output        = Column(Float)
    latency_ms    = Column(Float)
    model_version = Column(String)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("ML Service started, DB tables created")
    yield
    logger.info("ML Service shutting down")

app = FastAPI(title="ML Service", version="1.0.0", lifespan=lifespan)

class PredictRequest(BaseModel):
    features: list[float]

class PredictResponse(BaseModel):
    prediction: float
    model_version: str
    latency_ms: float

MODEL_VERSION = "1.0.0"

def run_model(features: list[float]) -> float:
    """Dummy model: weighted sum."""
    weights = [0.5, 0.3, 0.2] + [0.1] * max(0, len(features) - 3)
    return sum(f * w for f, w in zip(features, weights))

@app.post("/api/v1/predict", response_model=PredictResponse)
async def predict(body: PredictRequest, request: Request):
    REQUEST_COUNT.inc()
    start = time.perf_counter()
    try:
        prediction = run_model(body.features)
        latency_ms = (time.perf_counter() - start) * 1000
        REQUEST_LATENCY.observe(latency_ms / 1000)

        logger.info(json.dumps({
            "event": "prediction",
            "input": body.features,
            "output": prediction,
            "latency_ms": round(latency_ms, 3),
            "model_version": MODEL_VERSION,
        }))

        with Session(engine) as session:
            session.add(PredictionLog(
                input_data=json.dumps(body.features),
                output=prediction,
                latency_ms=round(latency_ms, 3),
                model_version=MODEL_VERSION,
            ))
            session.commit()

        return PredictResponse(
            prediction=prediction,
            model_version=MODEL_VERSION,
            latency_ms=round(latency_ms, 3),
        )
    except Exception as exc:
        REQUEST_ERRORS.inc()
        logger.error(json.dumps({"event": "error", "detail": str(exc)}))
        raise

@app.get("/health")
async def health():
    return {"status": "healthy", "model_version": MODEL_VERSION}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
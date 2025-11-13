"""
Minimal FastAPI app exposing a Prometheus `/metrics` endpoint.

This lightweight app is intended for local/dev tests where the full
`app.main` imports (DB, MQTT, Celery, etc.) are too heavy or require
infrastructure that isn't available during unit tests.
"""
import time
from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="EVENT - Simple Metrics App")

# Basic Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total_simple', 'Total HTTP requests', ['method', 'path', 'status_code'])
REQUEST_LATENCY = Histogram('http_request_latency_seconds_simple', 'HTTP request latency seconds', ['method', 'path'])


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        REQUEST_COUNT.labels(request.method, request.url.path, '500').inc()
        raise

    duration = time.time() - start
    try:
        REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)
        REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
    except Exception:
        # Metrics should never break responses
        pass

    return response


@app.get("/")
def root():
    return {"message": "simple metrics app operational"}


@app.get("/metrics")
def metrics():
    try:
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
    except Exception:
        return JSONResponse(status_code=500, content={"error": "metrics generation failed"})

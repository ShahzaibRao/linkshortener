from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.health import router as health_router
from app.api.links import router as links_router

app = FastAPI(title="LinkShortener")

# Prometheus metrics: har request ginta hai, /metrics pe dikhata hai
Instrumentator().instrument(app).expose(app)

app.include_router(health_router)
app.include_router(links_router)


from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.health import router as health_router
from app.api.links import bloom, router as links_router
from app.repos import links_repo


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Redis ke sare codes filter mein daalo (purane links bhi pehchane jayen)
    count = 0
    for key in links_repo.client.scan_iter("link:*"):
        bloom.add(key.split(":", 1)[1])
        count += 1
    print(f"bloom ready: {count} codes, {bloom.stats()}")
    yield


app = FastAPI(title="LinkShortener", lifespan=lifespan)

# Prometheus metrics: har request ginta hai, /metrics pe dikhata hai
Instrumentator().instrument(app).expose(app)

app.include_router(health_router)
app.include_router(links_router)


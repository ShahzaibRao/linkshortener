import os
import secrets

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from prometheus_client import Counter
from pydantic import BaseModel, HttpUrl

from app.core.bloom import BloomFilter
from app.repos import links_repo

router = APIRouter()

# Filter on/off — A/B test ke liye (bina filter vs filter), bina code change ke
FILTER_ENABLED = os.environ.get("FILTER_ENABLED", "true").lower() == "true"

# App ki memory mein filter (har replica/worker ki apni copy — EP-4 HLD!)
bloom = BloomFilter(capacity=200000)

# Prometheus: filter ne kitne roke, kitne jaane diye
filter_decisions = Counter(
    "filter_decisions_total",
    "Bloom filter decisions",
    ["decision"],  # rejected = pakka nahi tha | passed = shayad hai
)


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str


class LinkStats(BaseModel):
    code: str
    url: str
    clicks: int
    unique_views: int


@router.post("/api/v1/links", response_model=ShortenResponse)
def shorten(req: ShortenRequest):
    code = secrets.token_urlsafe(6)[:8]
    while links_repo.code_exists(code):
        code = secrets.token_urlsafe(6)[:8]
    links_repo.save_link(code, str(req.url))
    if FILTER_ENABLED:
        bloom.add(code)  # naya code filter mein daalo
    return {"code": code, "short_url": f"http://127.0.0.1:8000/{code}"}


@router.get("/api/v1/links/{code}/stats", response_model=LinkStats)
def stats(code: str):
    url = links_repo.get_link(code)
    if url is None:
        raise HTTPException(status_code=404, detail="link not found")
    return {
        "code": code,
        "url": url,
        "clicks": links_repo.get_clicks(code),
        "unique_views": links_repo.get_unique_views(code),
    }


@router.get("/{code}")
def redirect(code: str, request: Request):
    # Filter: "pakka nahi hai" → Redis jaane ki zaroorat nahi, foran 404
    if FILTER_ENABLED:
        if code not in bloom:
            filter_decisions.labels(decision="rejected").inc()
            raise HTTPException(status_code=404, detail="link not found")
        filter_decisions.labels(decision="passed").inc()
    url = links_repo.get_link(code)
    if url is None:
        raise HTTPException(status_code=404, detail="link not found")
    links_repo.track_click(code)
    # Unique view: visitor ki ID HyperLogLog mein (duplicate apne aap ignore)
    # NOTE: nginx ke peeche sab requests ek hi IP se aati nazar aati hain,
    # is liye X-Visitor-Id header (real app mein cookie/user-id hoti hai)
    visitor = request.headers.get("x-visitor-id") or request.client.host
    links_repo.track_unique_view(code, visitor)
    return RedirectResponse(url=url, status_code=307)

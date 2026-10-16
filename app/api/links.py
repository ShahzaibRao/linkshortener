import secrets

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from app.repos import links_repo

router = APIRouter()


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str


class LinkStats(BaseModel):
    code: str
    url: str
    clicks: int


@router.post("/api/v1/links", response_model=ShortenResponse)
def shorten(req: ShortenRequest):
    code = secrets.token_urlsafe(6)[:8]
    while links_repo.code_exists(code):
        code = secrets.token_urlsafe(6)[:8]
    links_repo.save_link(code, str(req.url))
    return {"code": code, "short_url": f"http://127.0.0.1:8000/{code}"}


@router.get("/api/v1/links/{code}/stats", response_model=LinkStats)
def stats(code: str):
    url = links_repo.get_link(code)
    if url is None:
        raise HTTPException(status_code=404, detail="link not found")
    return {"code": code, "url": url, "clicks": links_repo.get_clicks(code)}


@router.get("/{code}")
def redirect(code: str):
    url = links_repo.get_link(code)
    if url is None:
        raise HTTPException(status_code=404, detail="link not found")
    links_repo.track_click(code)
    return RedirectResponse(url=url, status_code=307)

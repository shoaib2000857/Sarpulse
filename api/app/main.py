from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from . import __version__
from .config import settings
from .routers import sites
from .store import get_store

app = FastAPI(
    title="SARPulse API",
    version=__version__,
    description="Scientific evidence and Change Passport API for SARPulse (Team StarFire).",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(sites.router)


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok", "version": __version__, "sites": get_store().site_ids()}


frontend = Path(__file__).resolve().parents[2] / "web" / "dist"
if frontend.is_dir():
    app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")

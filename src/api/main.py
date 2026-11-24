"""Nifty 100 Financial Intelligence REST API Server."""
from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

# Ensure project root is always in sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

import src.api.routers.companies as companies
import src.api.routers.documents as documents
import src.api.routers.health as health
import src.api.routers.peers as peers
import src.api.routers.portfolio as portfolio
import src.api.routers.screener as screener
import src.api.routers.sectors as sectors
import src.api.routers.valuation as valuation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("api_server")

app = FastAPI(
    title="Nifty 100 Financial Intelligence API",
    description="Production-grade RESTful API for 92 Nifty 100 constituents with 30+ financial KPIs, peer ranking, and screener.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware (Internal use - all origins allowed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        "%s %s -> Status %d (Duration: %sms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# Include all routers under /api/v1 prefix
app.include_router(health.router, prefix="/api/v1")
app.include_router(companies.router, prefix="/api/v1")
app.include_router(screener.router, prefix="/api/v1")
app.include_router(sectors.router, prefix="/api/v1")
app.include_router(peers.router, prefix="/api/v1")
app.include_router(valuation.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")

# Mount publication reports directory for direct browser viewing & download
_reports_dir = _ROOT / "reports"
if _reports_dir.exists():
    app.mount("/reports", StaticFiles(directory=str(_reports_dir)), name="reports")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Silence browser favicon 404."""
    return Response(status_code=204)


@app.get("/api")
def api_info():
    """Return API metadata."""
    return {
        "message": "Nifty 100 Financial Intelligence Platform API v1.0",
        "documentation": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/")
def root(request: Request):
    """Serve visual Apple Native Stocks application to browser; JSON to API clients."""
    accept_header = request.headers.get("accept", "")
    html_file = _ROOT / "frontend" / "standalone.html"
    
    # If browser requests HTML and standalone.html exists, serve visual frontend directly
    if "text/html" in accept_header and html_file.exists():
        return FileResponse(html_file, media_type="text/html")

    return {
        "message": "Nifty 100 Financial Intelligence Platform API v1.0",
        "documentation": "/docs",
        "health": "/api/v1/health",
        "app_ui": "/app",
    }


@app.get("/app", include_in_schema=False)
def serve_app():
    """Direct route for Apple Native Stocks visual interface."""
    html_file = _ROOT / "frontend" / "standalone.html"
    if html_file.exists():
        return FileResponse(html_file, media_type="text/html")
    return HTMLResponse("<h1>Visual Frontend Not Found</h1>", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

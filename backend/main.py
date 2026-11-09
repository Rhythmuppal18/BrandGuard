import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from app.core.config import FRONTEND_DIST
from app.core.database import init_db
from app.api.endpoints import router as api_router

# Initialize database schema on startup
init_db()

app = FastAPI(
    title="BrandGuard API - Intelligent Pre-Publication Brand Governance",
    version="2.0.0",
    description="CodeTitans India 2026 Round 2 Build. Automated brand rules, citations, tracked changes diff, and human-in-the-loop signoff."
)

# GZip compression for ultra-fast transfers (Lighthouse Performance 95+)
app.add_middleware(GZipMiddleware, minimum_size=500)

# Enable CORS for flexible local and preview environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core API router
app.include_router(api_router)

# Embedded SVG Favicon for instant, zero-dependency 200 OK responses
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4"/>
      <stop offset="50%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#8b5cf6"/>
    </linearGradient>
  </defs>
  <rect width="48" height="48" rx="14" fill="#050811"/>
  <rect x="2" y="2" width="44" height="44" rx="12" fill="url(#bgGrad)" fill-opacity="0.18" stroke="url(#bgGrad)" stroke-width="1.5"/>
  <path d="M24 10L14 14V22C14 28.5 18.2 34.6 24 36C29.8 34.6 34 28.5 34 22V14L24 10Z" fill="url(#bgGrad)" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M20 23L23 26L28 20" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

@app.get("/favicon.svg", response_class=Response)
@app.get("/favicon.ico", response_class=Response)
def serve_favicon():
    return Response(
        content=FAVICON_SVG,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"}
    )

# Mount frontend build if it exists
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept api routes, docs or openapi
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            # Cache static assets for 1 year, HTML files for 0s
            is_asset = "/assets/" in str(file_path).replace("\\", "/") or file_path.suffix in [".js", ".css", ".svg", ".png", ".woff2"]
            cache_header = "public, max-age=31536000, immutable" if is_asset else "no-cache"
            return FileResponse(file_path, headers={"Cache-Control": cache_header})
        return FileResponse(FRONTEND_DIST / "index.html", headers={"Cache-Control": "no-cache"})
else:
    @app.get("/")
    def root():
        return {
            "service": "BrandGuard Governance Engine",
            "status": "online",
            "docs": "/docs",
            "api_health": "/api/health",
            "scenarios": "/api/scenarios"
        }

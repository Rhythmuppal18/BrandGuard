import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

# Mount frontend build if it exists
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept api routes or docs
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
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

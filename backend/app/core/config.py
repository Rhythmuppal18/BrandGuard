import os
import shutil
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security & Cryptographic Config
SECRET_KEY = os.environ.get("BRANDGUARD_SECRET_KEY", "brandguard-r3-enterprise-hmac-sha256-key-v3")
TOKEN_EXPIRY_HOURS = 24
DEFAULT_TENANT_ID = os.environ.get("BRANDGUARD_TENANT_ID", "tenant-apexpay-prod")

# Upload limits and validation
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_FILE_EXTENSIONS = {".docx", ".pdf", ".txt", ".png", ".jpg", ".jpeg", ".svg"}
ALLOWED_MIME_TYPES = {
    "text/plain",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/png",
    "image/jpeg",
    "image/svg+xml"
}

# CORS Allowed Origins
RAW_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000,https://brandguard-kappa.vercel.app"
)
ALLOWED_ORIGINS: List[str] = [origin.strip() for origin in RAW_ORIGINS.split(",") if origin.strip()]

# Storage Architecture
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DATA_DIR = Path("/tmp/brandguard_data")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR = DATA_DIR / "uploads"
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = DATA_DIR / "brandguard.db"

    # Pre-populate database with seed data if bundled db exists
    seed_db = BASE_DIR / "data" / "brandguard.db"
    if seed_db.exists() and not DB_PATH.exists():
        try:
            shutil.copy2(seed_db, DB_PATH)
        except Exception:
            pass
else:
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR = DATA_DIR / "uploads"
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = DATA_DIR / "brandguard.db"

FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

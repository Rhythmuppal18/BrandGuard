import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# In Vercel serverless environments, the filesystem is read-only except /tmp
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

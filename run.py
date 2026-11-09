import sys
import os
from pathlib import Path
import uvicorn

# Ensure backend directory is in Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

if __name__ == "__main__":
    print("=" * 65)
    print(" BrandGuard | AI Brand Governance Platform")
    print(" CodeTitans India 2026 — Round 2 Production Build")
    print(" Team WHO CARES? | Problem Statement by Inkloom AI")
    print("=" * 65)
    print("\nStarting unified server at: http://127.0.0.1:8000")
    print("Serving interactive UI and API on a single port.\n")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)


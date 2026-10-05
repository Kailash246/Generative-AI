import uvicorn
import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    print("=" * 65)
    print("[START] Starting Local GitHub Code Explainer - FastAPI Backend Server")
    print("[API DOCS] http://127.0.0.1:8000/docs")
    print("[HEALTH]   http://127.0.0.1:8000/api/health")
    print("=" * 65)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)

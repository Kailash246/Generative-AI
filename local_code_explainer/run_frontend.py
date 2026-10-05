import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
app_path = PROJECT_ROOT / "frontend" / "app.py"

if __name__ == "__main__":
    print("=" * 65)
    print("[START] Starting Local GitHub Code Explainer - Streamlit Frontend")
    print("[URL]   http://localhost:8501")
    print("=" * 65)
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    subprocess.run(cmd)

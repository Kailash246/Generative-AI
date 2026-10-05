import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.repo_processor import RepoProcessor
from backend.llm_engine import LocalLLMEngine

def test_full_pipeline():
    print("[TEST] Testing Full Local GenAI Pipeline...")
    processor = RepoProcessor()
    llm = LocalLLMEngine()

    test_url = "https://github.com/streamlit/demo-uber-nyc-pickups"
    print(f"[1/3] Cloning and analyzing {test_url}...")
    analysis = processor.analyze_repository(test_url)
    print(f"      Scanned {analysis.source_files_count} source files.")

    print(f"[2/3] Checking LLM configuration (Device: {llm.device})...")
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    print(f"      Selected Model: {model_name}")

    print("[3/3] Generating structured explanation (this may take a few moments on first run to download model weights)...")
    start = time.time()
    explanation = llm.generate_explanation(
        analysis=analysis,
        provider="transformers",
        model_name=model_name,
        max_tokens=600,
        temperature=0.3
    )
    elapsed = time.time() - start

    print(f"\n[SUCCESS] Explanation generated in {elapsed:.2f} seconds!")
    print("=" * 60)
    print(explanation)
    print("=" * 60)

if __name__ == "__main__":
    test_full_pipeline()

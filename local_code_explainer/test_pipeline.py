import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.repo_processor import RepoProcessor
from backend.models import RepoRequest

def test_repo_processor():
    print("[TEST] Testing RepoProcessor...")
    processor = RepoProcessor()
    
    # Test with a lightweight public repository
    test_url = "https://github.com/streamlit/demo-uber-nyc-pickups"
    print(f"Cloning and analyzing {test_url}...")
    
    analysis = processor.analyze_repository(test_url)
    print(f"[OK] Repository Name: {analysis.repo_name}")
    print(f"[OK] Total Source Files: {analysis.source_files_count}")
    print(f"[OK] Detected Languages: {analysis.detected_languages}")
    print(f"[OK] Extracted Files Count: {len(analysis.extracted_files)}")
    print("\nFile Tree Preview:")
    print(analysis.file_tree_str)
    
    print("\nSample Extracted File:")
    if analysis.extracted_files:
        print(f"Path: {analysis.extracted_files[0].path}")
        print(f"Lines: {analysis.extracted_files[0].line_count}")
        print("Content Snippet:\n", analysis.extracted_files[0].content[:200])

    print("\n[SUCCESS] RepoProcessor test passed successfully!")

if __name__ == "__main__":
    test_repo_processor()

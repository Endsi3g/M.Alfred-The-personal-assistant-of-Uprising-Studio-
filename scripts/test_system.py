import os
import sys
import json
import time
import requests
import asyncio
from pathlib import Path

# Fix paths
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

def test_backend():
    print("\n--- [Backend Test] ---")
    try:
        from core.llm_manager import UnifiedLLM
        config_path = ROOT_DIR / "config" / "api_keys.json"
        llm = UnifiedLLM(config_path)
        print("[OK] UnifiedLLM initialized.")
        
        # Test a simple prompt (simulated or real depending on API key)
        resp = llm.generate_content("gemini-2.5-flash-lite", "Say 'Online'")
        if "Online" in resp or len(resp) > 0:
            print(f"[OK] LLM response received: {resp[:20]}...")
        else:
            print("[FAIL] LLM returned empty response.")
    except Exception as e:
        print(f"[FAIL] Backend initialization or LLM test failed: {e}")

def test_frontend():
    print("\n--- [Frontend Test] ---")
    try:
        # Check if the process is running would be better, but we can check if the port is reachable
        # Note: web_ui usually runs on port 8000
        url = "http://localhost:8000"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                print(f"[OK] Frontend (Web UI) is UP at {url}")
            else:
                print(f"[WARN] Frontend at {url} returned status {resp.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"[INFO] Frontend (Web UI) is not currently running at {url}. This is normal if main.py isn't active.")
    except Exception as e:
        print(f"[FAIL] Frontend test failed: {e}")

def test_modules():
    print("\n--- [Modules Test] ---")
    modules = {
        "CoPaw": ROOT_DIR / "modules" / "copaw_lib",
        "Awesome-Skills": ROOT_DIR / "modules" / "awesome_skills",
        "SeleniumBase": ROOT_DIR / "modules" / "seleniumbase_lib"
    }
    for name, path in modules.items():
        if path.exists():
            print(f"[OK] {name} module found at {path.name}")
        else:
            print(f"[FAIL] {name} module missing!")

    # Test Skills Index
    idx_path = ROOT_DIR / "modules" / "awesome_skills" / "skills_index.json"
    if idx_path.exists():
        with open(idx_path, "r", encoding="utf-8") as f:
            idx = json.load(f)
            print(f"[OK] Skills Index found with {len(idx)} skills.")
    else:
        print("[FAIL] Skills Index missing! Run scripts/update_skills.py")

if __name__ == "__main__":
    print("====================================")
    print(" PROJECT ALFRED — FULL SYSTEM TEST")
    print("====================================")
    test_backend()
    test_frontend()
    test_modules()
    print("\n[Verification Complete]")

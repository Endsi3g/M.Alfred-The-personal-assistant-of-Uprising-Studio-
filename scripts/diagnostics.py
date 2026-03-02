import os
import sys
import json
import socket
import platform
import psutil
import asyncio
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}")

def check_dependencies():
    print_header("1. DEPENDENCY CHECK")
    try:
        import google.generativeai as genai
        print("[OK] google-generativeai")
    except ImportError:
        print("[FAIL] google-generativeai is missing")

    try:
        import ollama
        print("[OK] ollama")
    except ImportError:
        print("[FAIL] ollama is missing")

    try:
        import fastapi
        import uvicorn
        print("[OK] FastAPI & Uvicorn")
    except ImportError:
        print("[FAIL] FastAPI or Uvicorn is missing")

    try:
        import sounddevice
        print("[OK] sounddevice")
    except ImportError:
        print("[FAIL] sounddevice is missing (Voice features might be limited)")

def check_config():
    print_header("2. CONFIGURATION CHECK")
    config_path = Path("config/api_keys.json")
    if config_path.exists():
        with open(config_path, "r") as f:
            try:
                config = json.load(f)
                if config.get("gemini_api_key"):
                    print("[OK] Gemini API Key found")
                else:
                    print("[WARN] Gemini API Key is empty")
                print(f"[INFO] Ollama URL: {config.get('ollama_url', 'http://localhost:11434')}")
            except Exception as e:
                print(f"[FAIL] Error reading config: {e}")
    else:
        print("[WARN] config/api_keys.json not found. System will prompt for setup on first launch.")

def check_network():
    print_header("3. NETWORK & REMOTE ACCESS")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"[INFO] Hostname: {hostname}")
    print(f"[INFO] Local IP: {local_ip}")
    print(f"[INFO] Web UI expected at: http://{local_ip}:8000")
    print(f"[INFO] Internet Connection: ", end="")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("Connected")
    except OSError:
        print("Disconnected")

def check_system_load():
    print_header("4. SYSTEM HEALTH")
    print(f"[INFO] OS: {platform.system()} {platform.release()}")
    print(f"[INFO] CPU Usage: {psutil.cpu_percent()}%")
    print(f"[INFO] RAM Usage: {psutil.virtual_memory().percent}%")
    print(f"[INFO] Disk Usage: {psutil.disk_usage('/').percent}%")

async def run_diagnostics():
    print("Initializing MARK XXX Diagnostics...")
    check_dependencies()
    check_config()
    check_network()
    # Check Integrated Modules
    print("\n[--- Integrated Modules ---]")
    modules = ["modules/copaw_lib", "modules/awesome_skills", "modules/seleniumbase_lib"]
    for mod in modules:
        path = Path(mod)
        if path.exists():
            print(f"[OK] {mod} found.")
        else:
            print(f"[FAIL] {mod} missing.")

    check_system_load()
    print_header("DIAGNOSTICS COMPLETE")
    print("If you see [FAIL], please run 'python setup.py' or install missing packages via pip.")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())

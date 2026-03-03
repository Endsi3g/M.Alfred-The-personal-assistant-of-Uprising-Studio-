import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT_DIR / "modules" / "awesome_skills"

def update_skills():
    print("[UPDATE] Updating Alfred's Skills Catalog...")
    
    # 1. Ensure PyYAML is installed
    try:
        import yaml
    except ImportError:
        print("[SETUP] Installing PyYAML...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyYAML"], check=True)

    # 2. Run the generator script
    script_path = SKILLS_DIR / "scripts" / "generate_index.py"
    if not script_path.exists():
        print(f"[ERROR] Could not find generator at {script_path}")
        return

    print("[INDEX] Re-indexing skills...")
    subprocess.run([sys.executable, str(script_path)], cwd=str(SKILLS_DIR), check=True)
    
    print("[OK] Skills Index successfully updated.")

if __name__ == "__main__":
    update_skills()

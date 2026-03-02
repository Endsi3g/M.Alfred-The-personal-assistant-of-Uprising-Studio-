import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT_DIR / "modules" / "awesome_skills"

def update_skills():
    print("🚀 Updating Alfred's Skills Catalog...")
    
    # 1. Ensure PyYAML is installed
    try:
        import yaml
    except ImportError:
        print("🔧 Installing PyYAML...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyYAML"], check=True)

    # 2. Run the generator script
    script_path = SKILLS_DIR / "scripts" / "generate_index.py"
    if not script_path.exists():
        print(f"❌ Could not find generator at {script_path}")
        return

    print("🏗️ Re-indexing skills...")
    subprocess.run([sys.executable, str(script_path)], cwd=str(SKILLS_DIR), check=True)
    
    print("✅ Skills Index successfully updated.")

if __name__ == "__main__":
    update_skills()

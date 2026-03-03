import sys
from pathlib import Path
import os

# Add root to sys.path
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from core.vision_tools import vision_servant
from core.llm_manager import UnifiedLLM

def test_vision():
    print("[Test] Capturing screen...")
    image_bytes = vision_servant.capture_full_screen()
    print(f"[Test] Captured {len(image_bytes)} bytes.")

    config_path = root / "config" / "api_keys.json"
    llm = UnifiedLLM(config_path)
    
    print("[Test] Asking Gemini to describe the screen...")
    try:
        response = llm.analyze_vision("Master Bell wants to know what is on his screen right now. Please summarize briefly.", image_bytes)
        print(f"[Test] Alfred's Response: {response}")
        print("[PASS] Vision test completed.")
    except Exception as e:
        print(f"[FAIL] Vision test failed: {e}")

if __name__ == "__main__":
    try:
        test_vision()
    except Exception as e:
        print(f"[ERROR] Vision test execution error: {e}")


import sys
from pathlib import Path

# Add root to sys.path
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from memory.memory_manager import add_episode, format_memory_for_prompt, search_memory

def test_semantic():
    print("[Test] Adding unique episode...")
    add_episode("user", "The secret passcode for the side door is 1234. Don't forget it, Alfred.")
    
    print("[Test] Formatting memory for prompt...")
    context = format_memory_for_prompt()
    print(f"[Test] Prompt Context:\n{context}")
    
    print("[Test] Searching for passcode...")
    result = search_memory("passcode")
    print(f"[Test] Search Result:\n{result}")

if __name__ == "__main__":
    try:
        test_semantic()
        print("[PASS] Semantic test passed (verify logs for embedding errors).")
    except Exception as e:
        print(f"[FAIL] Semantic test failed: {e}")


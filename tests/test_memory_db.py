import sys
from pathlib import Path

# Add root to sys.path
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from memory.memory_db import db_manager

def test_db():
    print("[Test] Testing long-term facts...")
    db_manager.upsert_fact("identity", "name", "Master Bell")
    db_manager.upsert_fact("preferences", "tea", "Earl Grey")
    
    facts = db_manager.get_facts()
    print(f"[Test] Retrieved facts: {facts}")
    
    print("[Test] Testing episodic memory...")
    db_manager.add_episode("test_session", "user", "Hello Alfred, how are you today?")
    db_manager.add_episode("test_session", "alfred", "I am functioning within normal parameters, Master Bell.")
    
    recent = db_manager.get_recent_episodes(limit=2)
    print(f"[Test] Recent episodes: {recent}")

if __name__ == "__main__":
    try:
        test_db()
        print("[PASS] DB test passed.")
    except Exception as e:
        print(f"[FAIL] DB test failed: {e}")


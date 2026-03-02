import asyncio
import sys
import os
from pathlib import Path

# Setup environment
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.multi_agent import mission_control

async def test_delegation():
    print("--- Initializing Alfred Tactical Agency Verification ---")
    
    # Mission 1: System Info (should go to Ops)
    print("\nMission 1: 'Alfred, what is the current system volume and are the services running?'")
    res1 = await mission_control.execute_mission("what is the current system volume and are the services running?")
    print(f"Response: {res1}")

    # Mission 2: Web Research (should go to Web)
    print("\nMission 2: 'Alfred, find the latest news about Master Bell's project.'")
    res2 = await mission_control.execute_mission("find the latest news about Master Bell's project.")
    print(f"Response: {res2}")

    print("\n[SUCCESS] Verification mission complete.")

if __name__ == "__main__":
    asyncio.run(test_delegation())

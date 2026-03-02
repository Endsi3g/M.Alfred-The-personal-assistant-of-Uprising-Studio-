import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.llm_manager import UnifiedLLM

async def test_fallback():
    # Path to a dummy or real config
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "api_keys.json"
    
    llm = UnifiedLLM(config_path)
    
    print("Testing LLM generation...")
    # This will try Gemini and then Ollama
    result = llm.generate_content(
        model_name="gemini-2.5-flash-lite",
        prompt="Tell me a joke about JARVIS.",
        system_instruction="You are a helpful assistant."
    )
    
    print(f"\nResult:\n{result}\n")
    
    if "Error" in result:
        print("[-] Test failed: Both Gemini and Ollama failed.")
        print("Note: This is expected if Gemini API key is not set AND Ollama is not running.")
    else:
        print("[+] Test passed: Received a response.")

if __name__ == "__main__":
    asyncio.run(test_fallback())

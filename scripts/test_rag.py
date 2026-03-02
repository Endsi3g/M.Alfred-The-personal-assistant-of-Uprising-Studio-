import sys
import os
from pathlib import Path

# Adjust path to find core
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.rag_service import retriever

def run_rag_test():
    print("=== Alfred RAG Intelligence Test ===")
    queries = [
        "How can I do pentesting?",
        "Help me with a React app",
        "I need building an agent"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        context = retriever.get_tactical_context(q)
        if context:
            print(context)
        else:
            print("[INFO] No specific skills found for this query.")

if __name__ == "__main__":
    run_rag_test()

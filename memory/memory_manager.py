import json
from threading import Lock
from pathlib import Path
import sys
import uuid
from .memory_db import db_manager
from core.embedding_service import embedder


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR    = get_base_dir()
_lock       = Lock()
_session_id = str(uuid.uuid4())

MAX_VALUE_LENGTH = 500  

def load_memory() -> dict:
    """
    Loads all facts from the SQLite DB and returns them as a structured dict.
    """
    facts = db_manager.get_facts()
    memory = {
        "identity":      {},
        "preferences":   {},
        "relationships": {},
        "notes":         {}
    }
    
    for category, key, value in facts:
        if category not in memory:
            memory[category] = {}
        memory[category][key] = {"value": value}
        
    return memory


def save_memory(memory: dict) -> None:
    """
    Saves the structured memory dict back to SQLite.
    """
    for category, items in memory.items():
        if not isinstance(items, dict):
            continue
        for key, entry in items.items():
            value = entry.get("value") if isinstance(entry, dict) else entry
            if value:
                db_manager.upsert_fact(category, key, str(value))


def update_memory(memory_update: dict) -> dict:
    """
    Updates the persistent memory with new facts.
    """
    if not isinstance(memory_update, dict) or not memory_update:
        return load_memory()

    with _lock:
        for category, items in memory_update.items():
            if not isinstance(items, dict):
                continue
            for key, value in items.items():
                # Extract value if it's a nested dict with 'value' key
                actual_value = value.get("value") if isinstance(value, dict) else value
                if actual_value:
                    db_manager.upsert_fact(category, key, str(actual_value))
                    print(f"[Memory] 💾 SQL Saved: {category}.{key}")

    return load_memory()


def add_episode(role: str, content: str, use_embedding: bool = True):
    """
    Saves a conversation turn to episodic memory.
    """
    embedding = None
    if use_embedding and len(content) > 10:
        embedding = embedder.get_embedding(content)
    
    db_manager.add_episode(_session_id, role, content, embedding)


def format_memory_for_prompt(memory: dict | None = None) -> str:
    """
    Formats the most relevant long-term facts and recent episodes for the LLM prompt.
    """
    if memory is None:
        memory = load_memory()

    lines = []

    # Identity (High Priority)
    identity = memory.get("identity", {})
    for key in ["name", "age", "birthday", "city"]:
        val = identity.get(key, {}).get("value")
        if val: lines.append(f"{key.title()}: {val}")

    # Preferences & Relationships (Limit 5 each)
    for cat in ["preferences", "relationships", "notes"]:
        items = memory.get(cat, {})
        for i, (key, entry) in enumerate(items.items()):
            if i >= 5: break
            val = entry.get("value") if isinstance(entry, dict) else entry
            if val: lines.append(f"{cat[:-1].title()}: {key.replace('_', ' ')} = {val}")

    # Recent Episodic Context
    recent = db_manager.get_recent_episodes(limit=5)
    context_lines = []
    if recent:
        context_lines.append("\n[RECENT CONVERSATION]")
        for role, content in recent:
            short_content = content[:100] + "..." if len(content) > 100 else content
            context_lines.append(f"- {role.title()}: {short_content}")

    if not lines and not context_lines:
        return ""

    result = "[USER MEMORY STATS]\n" + "\n".join(f"- {l}" for l in lines)
    if context_lines:
        result += "\n" + "\n".join(context_lines)
        
    return result + "\n"

def search_memory(query: str) -> str:
    """
    Performs a simple text search over episodes as a starting point.
    """
    results = db_manager.search_episodes_by_text(query)
    if not results:
        return "No past interactions found regarding this query."
    
    output = [f"Found {len(results)} past interactions:"]
    for role, content, ts in results:
        output.append(f"[{ts}] {role.title()}: {content}")
    
    return "\n".join(output)

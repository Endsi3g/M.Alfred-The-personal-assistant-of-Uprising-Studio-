import sqlite3
import json
from pathlib import Path
import sys
from datetime import datetime

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

DB_PATH = get_base_dir() / "memory" / "alfred_memory.db"

class MemoryDB:
    """
    Tactical SQLite database handler for Alfred's persistent memory.
    Handles long-term facts and episodic conversation context.
    """
    def __init__(self):
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(DB_PATH)

    def _init_db(self):
        with self._get_conn() as conn:
            # Table for long-term facts
            conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    key TEXT,
                    value TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, key)
                )
            """)
            # Table for conversation episodes
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    embedding BLOB,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def upsert_fact(self, category: str, key: str, value: str):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO long_term (category, key, value, timestamp)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(category, key) DO UPDATE SET
                value = excluded.value,
                timestamp = CURRENT_TIMESTAMP
            """, (category, key, value))
            conn.commit()

    def get_facts(self, category: str = None) -> list:
        with self._get_conn() as conn:
            if category:
                cursor = conn.execute("SELECT category, key, value FROM long_term WHERE category = ?", (category,))
            else:
                cursor = conn.execute("SELECT category, key, value FROM long_term")
            return cursor.fetchall()

    def add_episode(self, session_id: str, role: str, content: str, embedding: list = None):
        emb_blob = json.dumps(embedding).encode('utf-8') if embedding else None
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO episodes (session_id, role, content, embedding)
                VALUES (?, ?, ?, ?)
            """, (session_id, role, content, emb_blob))
            conn.commit()

    def get_recent_episodes(self, limit: int = 10) -> list:

        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT role, content FROM episodes 
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            return cursor.fetchall()[::-1] # Chronological order

    def search_episodes_by_text(self, query: str, limit: int = 5) -> list:
        # Simple text search for now (fallback for semantic search)
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT role, content, timestamp FROM episodes
                WHERE content LIKE ?
                ORDER BY timestamp DESC LIMIT ?
            """, (f"%{query}%", limit))
            return cursor.fetchall()

# Initialize DB
db_manager = MemoryDB()

from google import genai
import json
from pathlib import Path
import sys

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

class EmbeddingService:
    """
    Tactical service for generating semantic embeddings.
    Used for episodic memory search and retrieval.
    """
    def __init__(self, api_config_path: Path = None):
        if not api_config_path:
            api_config_path = get_base_dir() / "config" / "api_keys.json"
        
        self.api_config_path = api_config_path

        self._load_config()
        self.client = None
        if self.gemini_api_key:
            self.client = genai.Client(api_key=self.gemini_api_key)

    def _load_config(self):
        try:
            with open(self.api_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.gemini_api_key = config.get("gemini_api_key")
        except Exception:
            self.gemini_api_key = None

    def get_embedding(self, text: str) -> list[float]:
        """
        Generates an embedding for the given text using text-embedding-004.
        """
        if not self.client:
            print("[Embedding] Error: Client not initialized.")
            return []

        try:
            response = self.client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"[Embedding] Error generating embedding: {e}")
            return []

# Singleton instance
embedder = EmbeddingService()

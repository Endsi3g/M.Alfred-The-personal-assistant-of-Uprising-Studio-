import json
import os
import traceback
from pathlib import Path
from google import genai
import ollama

class UnifiedLLM:
    def __init__(self, api_config_path: Path):
        self.api_config_path = api_config_path
        self._load_config()
        self.client = None
        self._setup_gemini()
        # Model rotation sequence to maximize free-tier limits
        self.model_rotation = ["gemini-2.5-flash", "gemini-2.0-flash-lite-preview-02-05", "gemini-1.5-flash"]

    def _load_config(self):
        try:
            with open(self.api_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.gemini_api_key = config.get("gemini_api_key")
                self.ollama_url = config.get("ollama_url", "http://localhost:11434")
                self.ollama_model = config.get("ollama_model", "llama3")
        except Exception:
            self.gemini_api_key = None
            self.ollama_url = "http://localhost:11434"
            self.ollama_model = "llama3"

    def _setup_gemini(self):
        if self.gemini_api_key:
            try:
                self.client = genai.Client(api_key=self.gemini_api_key)
            except Exception as e:
                print(f"[UnifiedLLM] Gemini Client Init Error: {e}")

    def generate_content(self, model_name: str, prompt: str, system_instruction: str = None) -> str:
        # Try Gemini First with Rotation
        if self.client:
            test_models = [model_name] + [m for m in self.model_rotation if m != model_name]
            
            for m_name in test_models:
                try:
                    response = self.client.models.generate_content(
                        model=m_name,
                        contents=prompt,
                        config={'system_instruction': system_instruction} if system_instruction else None
                    )
                    return response.text
                except Exception as e:
                    print(f"[UnifiedLLM] Model {m_name} failed: {e}")
                    continue
            
            print("[UnifiedLLM] All Gemini models exhausted. Falling back to Ollama...")
        
        # Fallback to Ollama
        try:
            client = ollama.Client(host=self.ollama_url)
            messages = []
            if system_instruction:
                messages.append({'role': 'system', 'content': system_instruction})
            messages.append({'role': 'user', 'content': prompt})
            
            response = client.chat(model=self.ollama_model, messages=messages)
            return response['message']['content']
        except Exception as e:
            print(f"[UnifiedLLM] Ollama Error: {e}")
            return "Error: Both Gemini and Ollama failed to respond."

    def analyze_vision(self, prompt: str, image_bytes: bytes) -> str:
        """
        Uses Gemini to analyze an image (screen capture).
        """
        if not self.client:
            return "Error: Gemini client not initialized for vision."

        try:
            # We use gemini-1.5-flash for vision as it is fast and capable
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    prompt,
                    {'mime_type': 'image/png', 'data': image_bytes}
                ]
            )
            return response.text
        except Exception as e:
            print(f"[UnifiedLLM] Vision Analysis Error: {e}")
            return f"Error analyzing vision: {e}"

    def list_models(self):

        # Specific models for Gemini/Ollama could be handled here if needed
        pass

import json
import os
import traceback
from pathlib import Path
import google.generativeai as genai
import ollama

class UnifiedLLM:
    def __init__(self, api_config_path: Path):
        self.api_config_path = api_config_path
        self._load_config()
        self._setup_gemini()
        # Model rotation sequence to maximize free-tier limits (20 req/day per model)
        self.model_rotation = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-1.5-flash"]

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
            genai.configure(api_key=self.gemini_api_key)

    def generate_content(self, model_name: str, prompt: str, system_instruction: str = None) -> str:
        # Try Gemini First with Rotation
        if self.gemini_api_key:
            # If the requested model fails, try others in the rotation
            test_models = [model_name] + [m for m in self.model_rotation if m != model_name]
            
            for m_name in test_models:
                try:
                    model = genai.GenerativeModel(model_name=m_name, system_instruction=system_instruction)
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    print(f"[UnifiedLLM] Model {m_name} failed or limit reached: {e}")
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

    def list_models(self):
        # Specific models for Gemini/Ollama could be handled here if needed
        pass

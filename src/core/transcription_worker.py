import threading
import time
import io
import wave
import sounddevice as sd
import numpy as np
import traceback
from pathlib import Path
from google import genai

# Sliding window holding the last N transcribed chunks
_transcript_buffer = []
_BUFFER_MAX_ITEMS = 6 # e.g. 6 chunks of 10s = 60s of context

def get_live_transcript() -> str:
    """Returns the concatenated transcript text of the last N seconds."""
    return " ".join(_transcript_buffer).strip()

def _transcribe_chunk(wav_bytes: bytes, api_key: str):
    try:
        client = genai.Client(api_key=api_key)
        # We use Flash 1.5 to quickly transcribe the small audio chunk
        prompt = "Transcribe the following audio accurately. Reply ONLY with the transcript, or an empty string if there is no speech."
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                prompt,
                {"mime_type": "audio/wav", "data": wav_bytes}
            ]
        )
        
        text = response.text.strip()
        if text and len(text) > 2:
            _transcript_buffer.append(text)
            if len(_transcript_buffer) > _BUFFER_MAX_ITEMS:
                _transcript_buffer.pop(0)
            
            print(f"[LiveInsights] 🎤 {text}")
            
    except Exception as e:
        # Expected if API limits are hit or audio is pure silence
        pass

def _record_and_process(api_key: str):
    chunk_duration = 10 # seconds
    sample_rate = 16000
    
    while True:
        try:
            # Record audio chunk
            recording = sd.rec(int(chunk_duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
            sd.wait()
            
            # Convert to WAV bytes in memory
            buf = io.BytesIO()
            with wave.open(buf, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2) # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(recording.tobytes())
            
            wav_bytes = buf.getvalue()
            
            # Process in a sub-thread to immediately start the next recording chunk
            threading.Thread(target=_transcribe_chunk, args=(wav_bytes, api_key), daemon=True).start()
            
        except Exception as e:
            print(f"[LiveInsights] ⚠️ Audio Error: {e}")
            time.sleep(2)

def start_live_insights_worker():
    import json
    try:
        config_path = Path("config/api_keys.json")
        if not config_path.exists():
            return
            
        with open(config_path, "r", encoding="utf-8") as f:
            api_key = json.load(f).get("gemini_api_key")
            
        if api_key:
            threading.Thread(target=_record_and_process, args=(api_key,), daemon=True, name="LiveInsightsWorker").start()
            print("[LiveInsights] ✅ Passive audio transcription worker started.")
            
    except Exception as e:
        print(f"[LiveInsights] ⚠️ Initialization Error: {e}")

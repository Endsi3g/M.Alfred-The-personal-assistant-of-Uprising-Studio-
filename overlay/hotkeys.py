# overlay/hotkeys.py
import keyboard
import threading
from PyQt6.QtCore import pyqtSignal, QObject

class CluelyHotkeys(QObject):
    """Hotkeys globaux = CMD+Enter même si Alfred web UI focusé"""
    
    assist_requested = pyqtSignal()
    visibility_toggled = pyqtSignal()
    context_cleared = pyqtSignal()
    chat_focus_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._running = False
        
    def start(self):
        if self._running: return
        self._running = True
        
        def listen():
            # CMD+Enter (Mac) usually maps to Ctrl+Enter on Windows or specialized keys
            # We will support both for maximum compatibility
            keyboard.add_hotkey("ctrl+enter", self._on_assist)
            keyboard.add_hotkey("ctrl+\\", self._on_toggle)
            keyboard.add_hotkey("ctrl+r", self._on_clear)
            keyboard.add_hotkey("ctrl+space", self._on_chat_focus)
            keyboard.wait()
            
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        print("[Hotkeys] ✅  Listening for Global Commands (Ctrl+Enter)")
        
    def _on_assist(self):
        self.assist_requested.emit()
        
    def _on_toggle(self):
        self.visibility_toggled.emit()
        
    def _on_clear(self):
        self.context_cleared.emit()

    def _on_chat_focus(self):
        self.chat_focus_requested.emit()

# overlay/alfred_overlay.py
import sys
import asyncio
import threading
import mss
import base64
from io import BytesIO
from PIL import Image
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPropertyAnimation
from overlay.command_bar import AlfredCommandBar
from overlay.response_panel import CluelyResponsePanel
from overlay.hotkeys import CluelyHotkeys
from overlay.stealth import AlfredStealth
from core.llm_manager import UnifiedLLM
from actions.computer_settings import computer_settings
from actions.browser_control import browser_control
from core.transcription_worker import get_live_transcript
from pathlib import Path

class AlfredOverlay:
    """The central HUD orchestrator (PyQt6 version)"""
    
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 1. UI Components
        self.bar = AlfredCommandBar()
        self.panel = CluelyResponsePanel()
        
        # Initial state (Cluely style: start invisible)
        self.bar.setWindowOpacity(0.0)
        self.panel.setWindowOpacity(0.0)
        
        # 2. Hotkeys
        self.hotkeys = CluelyHotkeys()
        self.hotkeys.assist_requested.connect(self.trigger_assist)
        self.hotkeys.visibility_toggled.connect(self.toggle_visibility)
        self.hotkeys.context_cleared.connect(self._clear_context)
        self.hotkeys.chat_focus_requested.connect(self.focus_chat)
        self.hotkeys.start()
        
        # 3. Stealth
        self.bar.pilot_toggled.connect(self._on_pilot_toggle)
        self.bar.command_submitted.connect(self._process_text_command)
        self.stealth = AlfredStealth(self.bar.winId())
        self.panel_stealth = AlfredStealth(self.panel.winId())

        # 4. Alfred Core
        config_path = Path("config/api_keys.json")
        self.llm = UnifiedLLM(config_path)
        
        # 5. Animations
        self.bar_anim = QPropertyAnimation(self.bar, b"windowOpacity")
        self.bar_anim.setDuration(150) # Cluely speed
        
        self.panel_anim = QPropertyAnimation(self.panel, b"windowOpacity")
        self.panel_anim.setDuration(150)

        self.show_hud()
        print("[Overlay] ✅ PyQt6 Cluely HUD Started with Animations.")

    def show_hud(self):
        self.bar.show()
        self.fade_to(self.bar, self.bar_anim, 1.0)

    def _on_pilot_toggle(self, enabled):
        msg = "Pilot Mode Activated" if enabled else "Pilot Mode Deactivated"
        self.panel.set_reasoning(msg)

    def focus_chat(self):
        self.show_hud() # Assuming show_overlay should call show_hud
        self.bar.chat_input.setFocus()

    def _process_text_command(self, text):
        self.show_hud() # Assuming show_overlay should call show_hud
        self.panel.set_reasoning(f"Processing command: {text}")
        
        # 1. Capture screen for context (same as trigger_assist)
        # Assuming stealth.get_screenshot_bytes() is a new method or a placeholder for _capture_screen
        screenshot_bytes = self._capture_screen() # Using existing _capture_screen for now
        
        # 2. Run in thread to avoid UI freeze
        threading.Thread(target=self._run_assist_sync, args=(text, screenshot_bytes), daemon=True).start()

    def hide_hud(self):
        self.fade_to(self.bar, self.bar_anim, 0.0)
        self.panel.hide()

    def fade_to(self, widget, anim, target):
        anim.stop()
        anim.setStartValue(widget.windowOpacity())
        anim.setEndValue(target)
        anim.start()

    def toggle_visibility(self):
        if self.bar.windowOpacity() > 0.5:
            self.hide_hud()
        else:
            self.show_hud()

    def set_click_through(self, enabled):
        """Allows clicks to pass through to apps beneath (Cluely style)"""
        for win in [self.bar, self.panel]:
            flags = win.windowFlags()
            if enabled:
                win.setWindowFlags(flags | Qt.WindowType.WindowTransparentForInput)
            else:
                win.setWindowFlags(flags & ~Qt.WindowType.WindowTransparentForInput)
            win.show() # Refresh flags

    def trigger_assist(self):
        print("[Overlay] ⚡ Assist Triggered via Global Shortcut")
        if self.bar.windowOpacity() < 0.1:
            self.show_hud()
        
        # Ensure interaction is enabled when assist is active
        self.set_click_through(False)
        
        threading.Thread(target=self._run_assist_sync, daemon=True).start()

    def _run_assist_sync(self):
        """Bridge to run async logic from a side-thread for the UI"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._perform_assist())

    async def _perform_assist(self):
        self.panel.clear()
        self.panel.setWindowOpacity(0.0)
        self.panel.show()
        self.fade_to(self.panel, self.panel_anim, 1.0)
        
        # Disable click-through so user can interact with the panel (e.g. scroll)
        self.set_click_through(False)
        
        self.panel.set_reasoning("Capturing context...")
        
        # 1. Capture Screen
        screenshot_bytes = self._capture_screen()
        
        # 2. Get Audio Context
        audio_context = get_live_transcript()
        
        # 3. Prepare Prompt
        pilot_status = "ENABLED" if self.bar.pilot_mode else "DISABLED"
        prompt = f"""
        [CONTEXT]
        Audio last 60s: {audio_context}
        Pilot Mode (Autonomous): {pilot_status}
        
        [INSTRUCTION]
        Analyze the provided screenshot and audio. 
        Speak as Alfred Pennyworth. Use <think> tags for your internal reasoning.
        
        [PILOT MODE PROTOCOL]
        If Pilot Mode is ENABLED and an action is needed:
        1. Suggest the action in your response.
        2. Append exactly: [ACTION: tool_name, parameters: {{...}}]
        
        Supported Tools:
        - computer_settings: {{'description': '...'}} (for volume, brightness, etc.)
        - browser_control: {{'action': 'go_to', 'url': '...'}} or {{'action': 'search', 'query': '...'}}
        """
        
        # 4. Stream from Gemini
        self.panel.set_reasoning("Analyzing with Gemini...")
        
        try:
            # Using the new streaming method
            full_response = ""
            for chunk in self.llm.stream_vision(prompt, screenshot_bytes):
                full_response += chunk
                
                # Update reasoning vs response in real-time
                if "<think>" in full_response:
                    parts = full_response.split("</think>")
                    reasoning = parts[0].replace("<think>", "").strip()
                    final = parts[1].strip() if len(parts) > 1 else "..."
                    self.panel.set_reasoning(reasoning)
                    self.panel.set_response(final)
                else:
                    self.panel.set_response(full_response)
            
            # 5. POST-PROCESS PILOT MODE (Cluely AI Action)
            if self.bar.pilot_mode and "[ACTION:" in full_response:
                self.panel.set_reasoning("Executing tactical action...")
                try:
                    # Extract Action: [ACTION: tool, parameters: {...}]
                    match = re.search(r"\[ACTION:\s*(\w+),\s*parameters:\s*(\{.*?\})\]", full_response, re.DOTALL)
                    if match:
                        tool_name = match.group(1)
                        params_str = match.group(2)
                        params = json.loads(params_str.replace("'", '"'))
                        
                        result = "Action triggered."
                        if tool_name == "computer_settings":
                            result = computer_settings(params)
                        elif tool_name == "browser_control":
                            result = browser_control(params)
                        
                        self.panel.set_response(f"{full_response}\n\n[ALFRED] Result: {result}")
                except Exception as e:
                    print(f"[Overlay] Action Parsing Error: {e}")
        
        except Exception as e:
            self.panel.set_response(f"⚠️ Error: {e}")
        
        # Re-enable click-through after assist if desired, 
        # but let's keep it interactive while the panel is shown.

    def _capture_screen(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1] # Primary monitor
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()

    @staticmethod
    def start():
        overlay = AlfredOverlay()
        sys.exit(overlay.app.exec())

if __name__ == "__main__":
    AlfredOverlay.start()

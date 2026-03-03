# overlay/stealth.py
import ctypes
from ctypes import wintypes

class AlfredStealth:
    """Cluely Windows undetectability EXACT"""
    
    DWMWA_EXCLUDED_FROM_CAPTURE = 0x200002
    
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self._apply_stealth()
        
    def _apply_stealth(self):
        """Rend invisible aux captures Zoom/Teams via DWM Attribute"""
        try:
            # hwnd must be the integer window handle
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                int(self.hwnd),
                self.DWMWA_EXCLUDED_FROM_CAPTURE,
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int)
            )
        except Exception as e:
            print(f"[Stealth] ⚠️  Could not apply DWM stealth: {e}")

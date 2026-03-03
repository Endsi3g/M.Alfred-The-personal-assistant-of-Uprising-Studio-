import mss
import io
from PIL import Image

class ScreenCap:
    """
    Tactical screen capture utility for Alfred's vision.
    Provides methods to capture screen content for VLM analysis.
    """
    def __init__(self):
        self.sct = mss.mss()

    def capture_full_screen(self) -> bytes:
        """
        Captures the entire screen and returns it as PNG bytes.
        """
        screenshot = self.sct.grab(self.sct.monitors[1])  # Primary monitor
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    def capture_region(self, left: int, top: int, width: int, height: int) -> bytes:
        """
        Captures a specific region of the screen and returns it as PNG bytes.
        """
        monitor = {"top": top, "left": left, "width": width, "height": height}
        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

# Singleton for quick access
vision_servant = ScreenCap()

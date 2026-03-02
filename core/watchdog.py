import threading
import time
import socket
import pystray
from PIL import Image, ImageDraw
from pathlib import Path

class AlfredWatchdog:
    """
    Resident service that monitors system health and provides a tray presence.
    Part of Project B.E.L.L. (Milestone 1).
    """
    def __init__(self):
        self.icon = None
        self.stop_event = threading.Event()
        self.status = "Initializing..."
        self.connection_ok = False

    def _create_image(self, color1, color2):
        # Create a simple Bat-Shield inspired icon
        width, height = 64, 64
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.ellipse([8, 8, 56, 56], fill=color2, outline="black")
        # Draw a simple 'A' for Alfred
        dc.text((24, 20), "B", fill=color1)
        return image

    def _check_connectivity(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def _on_quit(self, icon, item):
        self.stop_event.set()
        icon.stop()

    def _on_open_ui(self, icon, item):
        import webbrowser
        webbrowser.open("http://localhost:8000")

    def monitor_loop(self):
        while not self.stop_event.is_set():
            self.connection_ok = self._check_connectivity()
            self.status = "ONLINE" if self.connection_ok else "OFFLINE (Fallback Active)"
            
            if self.icon:
                self.icon.title = f"Alfred: {self.status}"
            
            time.sleep(10)

    def start(self):
        # Create Tray Icon
        image = self._create_image("black", "#FFD700") # Gold/Black
        menu = pystray.Menu(
            pystray.MenuItem("Open Command Center", self._on_open_ui),
            pystray.MenuItem("Diagnostics", lambda: print("Diagnostics triggered")),
            pystray.MenuItem("Quit", self._on_quit)
        )
        self.icon = pystray.Icon("Alfred", image, "Alfred: STANDING BY", menu)
        
        # Start Monitor Thread
        threading.Thread(target=self.monitor_loop, daemon=True).start()
        
        # Run Tray (Blocking)
        self.icon.run()

if __name__ == "__main__":
    watchdog = AlfredWatchdog()
    watchdog.start()

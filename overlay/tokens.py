# overlay/tokens.py
from PyQt6.QtGui import QColor

CLUELY_DESIGN_SYSTEM = {
    # Glassmorphism (exact Cluely values)
    "glass_bg": QColor(15, 15, 20, int(0.72 * 255)),
    "glass_border": QColor(255, 255, 255, int(0.13 * 255)),
    "text_primary": QColor(255, 255, 255, int(0.92 * 255)),
    "text_reasoning": QColor(255, 255, 255, int(0.38 * 255)),
    
    # Layout (Cluely measurements)
    "navbar_height": 48,
    "navbar_radius": 14,
    "drag_handle_width": 24,
    "button_size": 24,
    
    # Alfred Integration (Batman gold accents)
    "alfred_gold": "#D4AF37",
    "alfred_status": "#27AE60"
}

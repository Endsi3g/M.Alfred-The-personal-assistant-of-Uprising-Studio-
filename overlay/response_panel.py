# overlay/response_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextBrowser, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QColor
from overlay.tokens import CLUELY_DESIGN_SYSTEM

class CluelyResponsePanel(QWidget):
    """Réplique EXACTE Cluely response HUD: 16px blur, reasoning tokens"""
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._build_ui()
        self.reasoning_text = ""
        self.final_text = ""
        
    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(400)
        self.setMinimumHeight(100)
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # 1. REASONING BOX (Grayed out)
        self.reasoning_label = QLabel("")
        self.reasoning_label.setWordWrap(True)
        self.reasoning_label.setFont(QFont("Segoe UI", 9))
        self.reasoning_label.setStyleSheet(f"color: {CLUELY_DESIGN_SYSTEM['text_reasoning'].name(QColor.NameFormat.HexArgb)};")
        layout.addWidget(self.reasoning_label)
        
        # 2. FINAL TEXT BROWSER (Markdown-ready)
        self.response_browser = QTextBrowser()
        self.response_browser.setOpenExternalLinks(True)
        self.response_browser.setStyleSheet(f"""
            background: transparent;
            border: none;
            color: {CLUELY_DESIGN_SYSTEM['text_primary'].name(QColor.NameFormat.HexArgb)};
            font-size: 14px;
        """)
        layout.addWidget(self.response_browser)
        
    def set_reasoning(self, text):
        self.reasoning_text = text
        self.reasoning_label.setText(text)
        self._adjust_size()

    def set_response(self, text):
        self.final_text = text
        # Simple HTML substitution for markdown-like look
        html = text.replace('\n', '<br>')
        self.response_browser.setHtml(html)
        self._adjust_size()

    def clear(self):
        self.reasoning_text = ""
        self.final_text = ""
        self.reasoning_label.setText("")
        self.response_browser.clear()
        self.hide()

    def _adjust_size(self):
        # Auto-expand height based on content
        self.layout().activate()
        hint = self.layout().sizeHint()
        new_height = min(max(hint.height() + 20, 100), 600)
        self.setFixedHeight(new_height)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(self.rect().toRectF(), 14, 14)
        
        # Darker glass for text readability
        painter.fillPath(path, CLUELY_DESIGN_SYSTEM["glass_bg"])
        painter.setPen(CLUELY_DESIGN_SYSTEM["glass_border"])
        painter.drawPath(path)

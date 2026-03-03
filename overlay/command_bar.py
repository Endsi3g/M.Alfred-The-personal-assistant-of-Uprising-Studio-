from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, QApplication, QLineEdit)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QLinearGradient, QColor
import json, os
from overlay.tokens import CLUELY_DESIGN_SYSTEM

class DragHandle6Dots(QWidget):
    """The 6-dot drag handle icon common in Cluely"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 100))
        
        # Draw 2 columns of 3 dots
        dot_size = 3
        spacing = 5
        x_offsets = [6, 11]
        y_offsets = [6, 11, 16]
        
        for x in x_offsets:
            for y in y_offsets:
                painter.drawEllipse(x, y, dot_size, dot_size)

class AlfredCommandBar(QWidget):
    """Réplique EXACTE Cluely navbar: 48px, 6-dot drag, glassmorphisme"""
    
    assist_requested = pyqtSignal()  # Triggered by CMD+Enter hook (externally)
    pilot_toggled = pyqtSignal(bool)
    command_submitted = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.position_file = "config/overlay_pos.json"
        self._drag_pos = None
        self.session_time = 0
        self.pilot_mode = False
        self._setup_window()
        self._build_ui()
        self._start_timer()
        self._load_position()
        
    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedHeight(CLUELY_DESIGN_SYSTEM["navbar_height"])
        self.setMinimumWidth(320)
        
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)
        
        # 1. DRAG HANDLE
        self.drag_handle = DragHandle6Dots(self)
        layout.addWidget(self.drag_handle)
        
        # 2. PILOT TOGGLE (Lightning icon)
        self.pilot_btn = QPushButton("⚡")
        self.pilot_btn.setFixedSize(28, 28)
        self.pilot_btn.setCheckable(True)
        self.pilot_btn.setStyleSheet(self._get_btn_style(False))
        self.pilot_btn.clicked.connect(self._toggle_pilot)
        layout.addWidget(self.pilot_btn)
        
        # 3. SESSION TIMER
        self.timer_label = QLabel("00:00")
        self.timer_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.timer_label.setStyleSheet(f"color: {CLUELY_DESIGN_SYSTEM['alfred_gold']};")
        layout.addWidget(self.timer_label)
        
        # 3.5 CHAT INPUT
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask Alfred...")
        self.chat_input.setFixedWidth(180)
        self.chat_input.setStyleSheet(f"""
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: #FFFFFF;
            padding: 2px 8px;
            font-size: 11px;
        """)
        self.chat_input.returnPressed.connect(self._on_chat_submit)
        layout.addWidget(self.chat_input)

        # Spacer
        layout.addStretch()
        
        # 4. ALFRED STATUS
        self.status_label = QLabel("ALFRED: READY")
        self.status_label.setStyleSheet(f"""
            color: #FFFFFF; 
            font-size: 10px; font-weight: bold;
            letter-spacing: 1.5px;
            padding: 4px 12px;
            background: rgba(212,175,55,0.2);
            border: 1px solid {CLUELY_DESIGN_SYSTEM['alfred_gold']};
            border-radius: 12px;
        """)
        layout.addWidget(self.status_label)
        
        # 5. CLOSE
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet("color: #fff; background: transparent; border: none; font-size: 14px;")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)
        
    def _get_btn_style(self, active):
        bg = "rgba(255, 51, 102, 0.2)" if active else "transparent"
        color = "#ff3366" if active else "rgba(255,255,255,0.5)"
        return f"background: {bg}; border: none; border-radius: 6px; color: {color}; font-size: 16px;"

    def _toggle_pilot(self):
        self.pilot_mode = not self.pilot_mode
        self.pilot_btn.setStyleSheet(self._get_btn_style(self.pilot_mode))
        self.pilot_toggled.emit(self.pilot_mode)

    def _on_chat_submit(self):
        text = self.chat_input.text().strip()
        if text:
            self.command_submitted.emit(text)
            self.chat_input.clear()
            self.chat_input.clearFocus()

    def _start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.timer.start(1000)
        
    def _update_timer(self):
        self.session_time += 1
        m, s = divmod(self.session_time, 60)
        self.timer_label.setText(f"{m:02d}:{s:02d}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(self.rect().toRectF(), 14, 14)
        
        # Background
        painter.fillPath(path, CLUELY_DESIGN_SYSTEM["glass_bg"])
        
        # Border
        painter.setPen(CLUELY_DESIGN_SYSTEM["glass_border"])
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Simple any-area drag for safety, but we can restrict it to handle
            self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._save_position()

    def _load_position(self):
        if os.path.exists(self.position_file):
            try:
                with open(self.position_file, "r") as f:
                    pos = json.load(f)
                    self.move(pos.get("x", 100), pos.get("y", 100))
            except: pass

    def _save_position(self):
        os.makedirs("config", exist_ok=True)
        with open(self.position_file, "w") as f:
            json.dump({"x": self.x(), "y": self.y()}, f)

import math
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QLinearGradient,
    QPainter,
)
from PySide6.QtWidgets import QWidget

from wizard_cat.themes import get_theme
from wizard_cat.utils import resource_path


class CompactTimerWidget(QWidget):
    """Slightly larger Always-On-Top floating pill widget displaying live timer and glowing frame on new chat messages."""

    restore_requested = Signal()

    def __init__(self, parent=None, theme_key="wizard_purple"):
        super().__init__(parent)

        # Always-On-Top Frameless Window Setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(150, 46)
        self.drag_position = None

        self.theme_colors = get_theme(theme_key)
        self.timer_text = "25:00"
        self.session_type = "work"

        # Font setup
        font_id = QFontDatabase.addApplicationFont(
            resource_path("fonts/PressStart2P-Regular.ttf")
        )
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.timer_font = QFont(font_family, 10)
        else:
            self.timer_font = QFont("Arial", 13, QFont.Weight.Bold)

        # Glow Animation State
        self.is_glowing = False
        self.glow_angle = 0.0
        self.glow_timer = QTimer(self)
        self.glow_timer.setInterval(30)
        self.glow_timer.timeout.connect(self._animate_glow)

    def update_theme(self, theme_key: str):
        self.theme_colors = get_theme(theme_key)
        self.update()

    def set_timer_display(self, time_str: str, session_type: str = "work"):
        self.timer_text = time_str
        self.session_type = session_type
        self.update()

    def start_glow(self):
        """Start pulsing magical gold border glow animation."""
        if not self.is_glowing:
            self.is_glowing = True
            self.glow_timer.start()

    def stop_glow(self):
        """Stop glowing animation."""
        self.is_glowing = False
        self.glow_timer.stop()
        self.update()

    def _animate_glow(self):
        self.glow_angle += 0.08
        if self.glow_angle > 2 * math.pi:
            self.glow_angle -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = self.theme_colors

        rect = self.rect()

        # Render Glowing Frame Halo if glowing
        if self.is_glowing:
            glow_val = int((math.sin(self.glow_angle) + 1.0) / 2.0 * 180) + 70

            painter.setBrush(Qt.BrushStyle.NoBrush)
            for i in range(1, 6):
                alpha = int(glow_val * (1.0 - i / 6.0))
                painter.setPen(QColor(255, 217, 102, alpha))
                painter.drawRoundedRect(rect.adjusted(i, i, -i, -i), 14, 14)

        # Pill Background Gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(t["bg_gradient"][0]))
        gradient.setColorAt(1.0, QColor(t["bg_gradient"][2]))

        painter.setBrush(gradient)
        border_color = QColor(255, 217, 102) if self.is_glowing else QColor(t["border"])
        painter.setPen(border_color)
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 14, 14)

        # Perfectly Centered Hourglass Icon & Timer Text
        painter.setFont(self.timer_font)
        painter.setPen(QColor(t["text_primary"]))

        icon = "⏳" if self.session_type == "work" else "☕"
        display_text = f"{icon} {self.timer_text}"

        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            display_text,
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            self._press_start_time = event.timestamp()

    def mouseMoveEvent(self, event):
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and self.drag_position is not None
        ):
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Click to restore full window
            if hasattr(self, "_press_start_time"):
                dt = event.timestamp() - self._press_start_time
                if dt < 300:  # short click
                    self.stop_glow()
                    self.restore_requested.emit()
            self.drag_position = None

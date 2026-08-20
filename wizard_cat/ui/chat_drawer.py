import time
from typing import List, Dict

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QLinearGradient,
    QMovie,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from wizard_cat.themes import get_theme
from wizard_cat.utils import resource_path


class VirtualRoomCanvas(QWidget):
    """Embedded custom canvas displaying online room members (or solo cat) on a virtual room floor."""

    def __init__(self, parent=None, colors=None):
        super().__init__(parent)
        self.colors = colors or get_theme("wizard_purple")
        self.members: List[dict] = []
        self.reactions: List[dict] = []  # active floating emote bubbles

        self.setMinimumSize(320, 180)

        # Cat GIF Asset
        self.cat_movie = QMovie(resource_path("assets/cat/wizard_cat.gif"))
        self.cat_movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.cat_movie.frameChanged.connect(self.update)
        self.cat_movie.start()

        # Animation timer for floating reactions
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(40)
        self.anim_timer.timeout.connect(self._update_reactions)
        self.anim_timer.start()

    def set_members(self, member_list: List[dict]):
        self.members = member_list
        self.update()

    def add_reaction(self, username: str, emote: str):
        """Add a floating reaction bubble above a wizard's cat."""
        self.reactions.append({
            "username": username,
            "emote": emote,
            "y_offset": 0,
            "opacity": 1.0,
        })
        self.update()

    def _update_reactions(self):
        if not self.reactions:
            return

        to_remove = []
        for r in self.reactions:
            r["y_offset"] += 1.5
            r["opacity"] -= 0.02
            if r["opacity"] <= 0:
                to_remove.append(r)

        for r in to_remove:
            self.reactions.remove(r)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = self.colors

        # Floor Gradient (Cozy Dark Wood / Magic Room)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#120D1C"))
        gradient.setColorAt(0.5, QColor("#221833"))
        gradient.setColorAt(1.0, QColor("#1A1129"))

        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)

        # Floor Planks & Magical Sparkles
        painter.setPen(QColor(c["border"]).darker(150))
        for y in range(30, self.height(), 40):
            painter.drawLine(0, y, self.width(), y)

        sparkles = [(30, 40), (120, 25), (260, 35), (70, 140), (270, 150)]
        for sx, sy in sparkles:
            painter.setBrush(QColor(c["sparkles"]))
            painter.drawRect(sx, sy, 2, 2)

        if not self.members:
            # Solo Mode: Render 1 Cat in Center
            self._render_single_cat(painter, self.width() // 2, self.height() // 2 + 15, "WizardCat", 1, "FOCUSING", 0, 0)
            return

        # Render Cats side-by-side on Virtual Room Floor
        count = len(self.members)
        cat_w, cat_h = 60, 60

        # Calculate neat row positions across virtual floor
        positions = []
        cols = 3
        for i in range(count):
            r = i // cols
            col = i % cols
            row_count = min(cols, count - r * cols)
            x_step = self.width() / (row_count + 1)
            x = int((col + 1) * x_step)
            y = int(65 + r * 65)
            positions.append((x, y))

        current_frame = self.cat_movie.currentPixmap() if self.cat_movie.isValid() else QPixmap()

        for idx, member in enumerate(self.members):
            if idx >= len(positions):
                break

            cx, cy = positions[idx]
            name = member.get("username", "Wizard")
            lvl = member.get("level", 1)
            status = member.get("status", "FOCUSING")
            total_mins = member.get("total_focus_minutes", 0)
            session_mins = member.get("session_minutes", 0)

            self._render_cat_with_badge(painter, cx, cy, name, lvl, status, total_mins, session_mins, current_frame)

    def _render_single_cat(self, painter, cx, cy, name, lvl, status, total_mins, session_mins):
        current_frame = self.cat_movie.currentPixmap() if self.cat_movie.isValid() else QPixmap()
        cat_w, cat_h = 75, 75

        # Shadow under cat
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - 28, cy + cat_h // 2 - 8, 56, 14)

        # Cat Graphic
        if not current_frame.isNull():
            painter.drawPixmap(cx - cat_w // 2, cy - cat_h // 2, cat_w, cat_h, current_frame)

    def _render_cat_with_badge(self, painter, cx, cy, name, lvl, status, total_mins, session_mins, current_frame):
        c = self.colors
        cat_w, cat_h = 60, 60

        if total_mins < 60:
            total_str = f"{total_mins}m"
        else:
            total_str = f"{total_mins // 60}h {total_mins % 60}m"

        # Shadow under cat
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - 22, cy + cat_h // 2 - 6, 44, 12)

        # Cat Graphic
        if not current_frame.isNull():
            painter.drawPixmap(cx - cat_w // 2, cy - cat_h // 2, cat_w, cat_h, current_frame)

        # Floating Personal Study Stats Badge Above Cat
        bg_rect = QRectF(cx - 65, cy - cat_h // 2 - 32, 130, 30)
        painter.setBrush(QColor(c["input_bg"]))
        painter.setPen(QColor(c["border"]))
        painter.drawRoundedRect(bg_rect, 5, 5)

        # Username & Level
        painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))
        painter.setPen(QColor(c["accent"]))
        painter.drawText(
            QRectF(cx - 65, cy - cat_h // 2 - 30, 130, 13),
            Qt.AlignmentFlag.AlignCenter,
            f"🧙‍♂️ {name} (Lvl {lvl})",
        )

        # Personal Study Time Stat
        status_color = QColor(c["session_work"]) if status == "FOCUSING" else QColor(c["session_long"])
        painter.setPen(status_color)
        painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))

        if status == "FOCUSING":
            personal_stat_str = f"⏱️ Total: {total_str} ({session_mins}m)"
        else:
            personal_stat_str = f"☕ On Break ({total_str})"

        painter.drawText(
            QRectF(cx - 65, cy - cat_h // 2 - 16, 130, 13),
            Qt.AlignmentFlag.AlignCenter,
            personal_stat_str,
        )

        # Render Floating Reaction Bubbles
        for r in self.reactions:
            if r["username"] == name or r["username"] == "all":
                rx = cx
                ry = cy - cat_h // 2 - 40 - r["y_offset"]
                op = int(r["opacity"] * 255)
                if op > 0:
                    painter.setFont(QFont("Arial", 15))
                    painter.setPen(QColor(255, 255, 255, op))
                    painter.drawText(
                        QRectF(rx - 20, ry - 15, 40, 30),
                        Qt.AlignmentFlag.AlignCenter,
                        r["emote"],
                    )


class RoomChatDrawer(QDialog):
    """Pop-over window for sending reactions and chatting in an active room."""

    def __init__(self, parent=None, room_manager=None):
        super().__init__(parent)
        self.room_manager = room_manager
        self.setWindowTitle("Room Chat & Reactions")
        self.setFixedSize(320, 360)

        theme_key = getattr(parent, "theme_key", "wizard_purple")
        self.colors = get_theme(theme_key)
        self._apply_stylesheet()

        # Quick Reaction Emote Buttons
        emotes_layout = QHBoxLayout()
        emotes_label = QLabel("Reactions:")
        emotes_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        emotes_layout.addWidget(emotes_label)

        for emote in ["✨", "☕", "📚", "🪄", "❤️"]:
            btn = QPushButton(emote)
            btn.setFixedWidth(36)
            btn.clicked.connect(lambda ch, e=emote: self._send_reaction(e))
            emotes_layout.addWidget(btn)
        emotes_layout.addStretch()

        # Live Chat Section
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message in room chat...")
        self.chat_input.returnPressed.connect(self._send_chat)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._send_chat)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)

        # Assembly
        layout = QVBoxLayout()
        layout.addLayout(emotes_layout)
        layout.addSpacing(6)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        self.setLayout(layout)

        if self.room_manager:
            self.room_manager.chat_received.connect(self.add_chat_message)

    def add_chat_message(self, username: str, text: str, msg_type: str):
        if msg_type == "system":
            formatted = f"<i><b>system:</b> {username} {text}</i><br>"
        elif msg_type == "level_up":
            formatted = f"<b style='color: #FFD966;'>✨ {username}:</b> {text}<br>"
        elif msg_type == "reaction":
            formatted = f"<i><b>{username} sent {text}</b></i><br>"
        else:
            formatted = f"<b>{username}:</b> {text}<br>"

        self.chat_display.append(formatted)

    def _send_reaction(self, emote: str):
        if self.room_manager:
            self.room_manager.send_chat_message(emote, msg_type="reaction")

    def _send_chat(self):
        txt = self.chat_input.text().strip()
        if txt and self.room_manager:
            self.room_manager.send_chat_message(txt)
            self.chat_input.clear()

    def _apply_stylesheet(self):
        c = self.colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c['dialog_bg']};
                color: {c['text_secondary']};
            }}
            QLabel {{ color: {c['text_secondary']}; }}
            QTextEdit {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 4px;
                font-size: 11px;
            }}
            QLineEdit {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {c['dialog_bg']};
                color: {c['text_secondary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {c['accent_hover']};
                border: 1px solid {c['border_hover']};
                color: {c['text_primary']};
            }}
        """)

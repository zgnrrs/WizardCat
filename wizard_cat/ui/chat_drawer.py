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
    """Custom canvas displaying online room members as Wizard Cats gathered in a cozy virtual room."""

    def __init__(self, parent=None, colors=None):
        super().__init__(parent)
        self.colors = colors or get_theme("wizard_purple")
        self.members: List[dict] = []
        self.reactions: List[dict] = []  # active floating emote bubbles

        self.setMinimumSize(340, 260)

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
        for y in range(40, self.height(), 45):
            painter.drawLine(0, y, self.width(), y)

        sparkles = [(30, 50), (120, 30), (280, 45), (70, 210), (290, 200)]
        for sx, sy in sparkles:
            painter.setBrush(QColor(c["sparkles"]))
            painter.drawRect(sx, sy, 2, 2)

        if not self.members:
            # Empty Room Message
            painter.setFont(QFont("Arial", 10))
            painter.setPen(QColor(c["text_secondary"]))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Oda yükleniyor...\nKediniz ve arkadaşlarınız belirmek üzere! 🪄",
            )
            return

        # Render Cats on Virtual Room Floor
        count = len(self.members)
        cat_w, cat_h = 70, 70

        # Calculate position slots across virtual floor
        positions = []
        if count == 1:
            positions = [(self.width() // 2, self.height() // 2 + 10)]
        elif count == 2:
            positions = [
                (self.width() // 3, self.height() // 2 + 10),
                (2 * self.width() // 3, self.height() // 2 + 10),
            ]
        else:
            cols = min(3, count)
            rows = (count + cols - 1) // cols
            for i in range(count):
                r = i // cols
                col = i % cols
                x = int((col + 0.6) * (self.width() / cols))
                y = int(85 + r * 85)
                positions.append((x, y))

        current_frame = self.cat_movie.currentPixmap() if self.cat_movie.isValid() else QPixmap()

        for idx, member in enumerate(self.members):
            if idx >= len(positions):
                break

            cx, cy = positions[idx]
            name = member.get("username", "Wizard")
            lvl = member.get("level", 1)
            title = member.get("title", "")
            status = member.get("status", "FOCUSING")
            t_str = member.get("time_str", "25:00")

            # Shadow under cat
            painter.setBrush(QColor(0, 0, 0, 80))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(cx - 25, cy + cat_h // 2 - 8, 50, 14)

            # Cat Graphic
            if not current_frame.isNull():
                painter.drawPixmap(cx - cat_w // 2, cy - cat_h // 2, cat_w, cat_h, current_frame)

            # Floating Nametag & Prominent Timer Badge Above Cat
            bg_rect = QRectF(cx - 70, cy - cat_h // 2 - 38, 140, 34)
            painter.setBrush(QColor(c["input_bg"]))
            painter.setPen(QColor(c["border"]))
            painter.drawRoundedRect(bg_rect, 6, 6)

            # Username & Level
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            painter.setPen(QColor(c["accent"]))
            painter.drawText(
                QRectF(cx - 70, cy - cat_h // 2 - 36, 140, 15),
                Qt.AlignmentFlag.AlignCenter,
                f"🧙‍♂️ {name} (Lvl {lvl})",
            )

            # Status & Prominent Timer Display
            status_color = QColor(c["session_work"]) if status == "FOCUSING" else QColor(c["session_long"])
            painter.setPen(status_color)
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            timer_display = f"⏳ {t_str}" if t_str else f"{status}"
            painter.drawText(
                QRectF(cx - 70, cy - cat_h // 2 - 20, 140, 15),
                Qt.AlignmentFlag.AlignCenter,
                f"{status} • {timer_display}",
            )

            # Render Floating Reaction Bubbles
            for r in self.reactions:
                if r["username"] == name or r["username"] == "all":
                    rx = cx
                    ry = cy - cat_h // 2 - 45 - r["y_offset"]
                    op = int(r["opacity"] * 255)
                    if op > 0:
                        painter.setFont(QFont("Arial", 16))
                        painter.setPen(QColor(255, 255, 255, op))
                        painter.drawText(
                            QRectF(rx - 20, ry - 15, 40, 30),
                            Qt.AlignmentFlag.AlignCenter,
                            r["emote"],
                        )


class RoomPanel(QDialog):
    """Pop-out window displaying the Virtual Wizard Cat Study Lounge, live timer, and chat."""

    def __init__(self, parent=None, room_manager=None):
        super().__init__(parent)
        self.room_manager = room_manager
        self.setWindowTitle("Wizard Cat - Sanal Birlikte Çalışma Odası")
        self.setFixedSize(380, 520)

        theme_key = getattr(parent, "theme_key", "wizard_purple")
        self.colors = get_theme(theme_key)
        self._apply_stylesheet()

        # Room Code Header
        self.code_label = QLabel("Oda Kodu: -")
        self.code_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['accent']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)

        # Prominent Timer Readout Header
        self.timer_header_label = QLabel("⏳ --:--")
        self.timer_header_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text_primary']};
                font-size: 13px;
                font-weight: bold;
                background-color: {self.colors['input_bg']};
                border: 1px solid {self.colors['border']};
                border-radius: 4px;
                padding: 2px 6px;
            }}
        """)

        self.copy_btn = QPushButton("📋 Kopyala")
        self.copy_btn.clicked.connect(self._copy_code)

        self.leave_btn = QPushButton("🚪 Odadan Ayrıl")
        self.leave_btn.clicked.connect(self._leave_room)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.code_label)
        top_bar.addWidget(self.timer_header_label)
        top_bar.addStretch()
        top_bar.addWidget(self.copy_btn)
        top_bar.addWidget(self.leave_btn)

        # Virtual Room Canvas
        self.canvas = VirtualRoomCanvas(self, colors=self.colors)

        # Quick Reaction Emote Buttons
        emotes_layout = QHBoxLayout()
        emotes_label = QLabel("Reaksiyon:")
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
        self.chat_display.setFixedHeight(90)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Oda sohbetine yazın...")
        self.chat_input.returnPressed.connect(self._send_chat)

        send_btn = QPushButton("Gönder")
        send_btn.clicked.connect(self._send_chat)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)

        # Assembly
        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self.canvas)
        layout.addLayout(emotes_layout)
        layout.addSpacing(4)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        self.setLayout(layout)

        # Connect Signals
        if self.room_manager:
            self.room_manager.members_updated.connect(self.on_members_updated)
            self.room_manager.chat_received.connect(self.add_chat_message)
            self.room_manager.room_joined.connect(self.set_room_code)

    def set_room_code(self, code: str):
        self.code_label.setText(f"Oda Kodu: {code}")

    def on_members_updated(self, member_list: list):
        self.canvas.set_members(member_list)
        if self.room_manager:
            for m in member_list:
                if m.get("user_id") == self.room_manager.user_id:
                    status = m.get("status", "FOCUSING")
                    t_str = m.get("time_str", "--:--")
                    self.timer_header_label.setText(f"⏳ {t_str} [{status}]")
                    break

    def add_chat_message(self, username: str, text: str, msg_type: str):
        if msg_type == "reaction":
            self.canvas.add_reaction(username, text)
            return

        if msg_type == "system":
            formatted = f"<i><b>system:</b> {username} {text}</i><br>"
        elif msg_type == "level_up":
            formatted = f"<b style='color: #FFD966;'>✨ {username}:</b> {text}<br>"
            self.canvas.add_reaction(username, "✨")
        else:
            formatted = f"<b>{username}:</b> {text}<br>"

        self.chat_display.append(formatted)

    def _send_reaction(self, emote: str):
        if self.room_manager:
            self.room_manager.send_chat_message(emote, msg_type="reaction")
            self.canvas.add_reaction(self.room_manager.username, emote)

    def _send_chat(self):
        txt = self.chat_input.text().strip()
        if txt and self.room_manager:
            self.room_manager.send_chat_message(txt)
            self.chat_input.clear()

    def _copy_code(self):
        if self.room_manager and self.room_manager.room_code:
            QGuiApplication.clipboard().setText(self.room_manager.room_code)
            self.copy_btn.setText("✓ Kopyalandı!")
            QGuiApplication.singleShot(2000, lambda: self.copy_btn.setText("📋 Kopyala"))

    def _leave_room(self):
        if self.room_manager:
            self.room_manager.leave_room()
        self.close()

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

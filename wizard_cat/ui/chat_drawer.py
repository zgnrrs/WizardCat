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
    """Canvas displaying all connected room members as animated Wizard Cats on a virtual room floor."""

    def __init__(self, parent=None, colors=None):
        super().__init__(parent)
        self.colors = colors or get_theme("wizard_purple")
        self.members: List[dict] = []
        self.reactions: List[dict] = []  # active floating emote bubbles

        self.setMinimumSize(360, 240)

        # Cat GIF Asset for all members
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

        sparkles = [(30, 50), (140, 30), (300, 45), (80, 190), (310, 200)]
        for sx, sy in sparkles:
            painter.setBrush(QColor(c["sparkles"]))
            painter.drawRect(sx, sy, 2, 2)

        if not self.members:
            # Connecting / Empty Room Message
            painter.setFont(QFont("Arial", 10))
            painter.setPen(QColor(c["text_secondary"]))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Connecting to study room...\nWizard cats will gather here as friends join! 🪄",
            )
            return

        # Render Animated Cats side-by-side on Virtual Room Floor
        count = len(self.members)
        cat_w, cat_h = 70, 70

        # Calculate neat row positions across virtual floor
        positions = []
        cols = 3
        for i in range(count):
            r = i // cols
            col = i % cols
            row_count = min(cols, count - r * cols)
            x_step = self.width() / (row_count + 1)
            x = int((col + 1) * x_step)
            y = int(80 + r * 85)
            positions.append((x, y))

        current_frame = self.cat_movie.currentPixmap() if self.cat_movie.isValid() else QPixmap()

        for idx, member in enumerate(self.members):
            if idx >= len(positions):
                break

            cx, cy = positions[idx]
            name = member.get("username", "Wizard")
            lvl = member.get("level", 1)
            status = member.get("status", "FOCUSING")

            # Personal study stats
            total_mins = member.get("total_focus_minutes", 0)
            session_mins = member.get("session_minutes", 0)

            if total_mins < 60:
                total_str = f"{total_mins}m"
            else:
                total_str = f"{total_mins // 60}h {total_mins % 60}m"

            # Shadow under cat
            painter.setBrush(QColor(0, 0, 0, 80))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(cx - 25, cy + cat_h // 2 - 8, 50, 14)

            # Animated Cat Graphic (Animated for all members)
            if not current_frame.isNull():
                painter.drawPixmap(cx - cat_w // 2, cy - cat_h // 2, cat_w, cat_h, current_frame)

            # Floating Personal Study Stats Badge Above/Below Cat
            bg_rect = QRectF(cx - 75, cy - cat_h // 2 - 36, 150, 32)
            painter.setBrush(QColor(c["input_bg"]))
            painter.setPen(QColor(c["border"]))
            painter.drawRoundedRect(bg_rect, 6, 6)

            # Username & Level
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            painter.setPen(QColor(c["accent"]))
            painter.drawText(
                QRectF(cx - 75, cy - cat_h // 2 - 34, 150, 14),
                Qt.AlignmentFlag.AlignCenter,
                f"🧙‍♂️ {name} (Lvl {lvl})",
            )

            # Personal Study Time Stat Worked
            status_color = QColor(c["session_work"]) if status == "FOCUSING" else QColor(c["session_long"])
            painter.setPen(status_color)
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))

            if status == "FOCUSING":
                personal_stat_str = f"⏱️ Total: {total_str} ({session_mins}m)"
            else:
                personal_stat_str = f"☕ On Break ({total_str})"

            painter.drawText(
                QRectF(cx - 75, cy - cat_h // 2 - 18, 150, 14),
                Qt.AlignmentFlag.AlignCenter,
                personal_stat_str,
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
    """Online Study Room Window featuring virtual cat floor, live chat, and full Pomodoro controls."""

    def __init__(self, main_window, room_manager=None):
        super().__init__()
        self.main_window = main_window
        self.room_manager = room_manager
        self.setWindowTitle("Wizard Cat - Online Study Room")
        self.setFixedSize(410, 620)

        theme_key = getattr(main_window, "theme_key", "wizard_purple")
        self.colors = get_theme(theme_key)
        self._apply_stylesheet()

        # Top Bar: Room Code, Copy, Leave
        self.code_label = QLabel("Room Code: -")
        self.code_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['accent']};
                font-size: 15px;
                font-weight: bold;
            }}
        """)

        self.copy_btn = QPushButton("📋 Copy Code")
        self.copy_btn.clicked.connect(self._copy_code)

        self.leave_btn = QPushButton("🚪 Leave Room")
        self.leave_btn.clicked.connect(self._leave_room)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.code_label)
        top_bar.addStretch()
        top_bar.addWidget(self.copy_btn)
        top_bar.addWidget(self.leave_btn)

        # Virtual Room Canvas
        self.canvas = VirtualRoomCanvas(self, colors=self.colors)

        # Reaction Emotes Bar
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

        # Live Chat Box
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFixedHeight(85)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message in room chat...")
        self.chat_input.returnPressed.connect(self._send_chat)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._send_chat)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)

        # Bottom Pomodoro Timer Control Section
        timer_box = QVBoxLayout()
        
        self.timer_readout = QLabel("25:00")
        self.timer_readout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_readout.setFont(main_window.timer_font)
        self.timer_readout.setStyleSheet(f"color: {self.colors['text_primary']};")

        self.session_label = QLabel("FOCUS")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setFont(main_window.small_font)
        self.session_label.setStyleSheet(f"color: {self.colors['session_work']}; font-weight: bold;")

        # Controls Buttons
        self.start_btn = QPushButton("▶")
        self.start_btn.setFixedSize(50, 32)
        self.start_btn.clicked.connect(self._toggle_timer)

        self.break_btn = QPushButton("☕")
        self.break_btn.setFixedSize(50, 32)
        self.break_btn.clicked.connect(self._toggle_break)

        self.reset_btn = QPushButton("↻")
        self.reset_btn.setFixedSize(36, 32)
        self.reset_btn.clicked.connect(self._reset_timer)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(36, 32)
        self.settings_btn.clicked.connect(self._open_settings)

        ctrl_layout = QHBoxLayout()
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(self.start_btn)
        ctrl_layout.addWidget(self.break_btn)
        ctrl_layout.addWidget(self.reset_btn)
        ctrl_layout.addWidget(self.settings_btn)
        ctrl_layout.addStretch()

        timer_box.addWidget(self.timer_readout)
        timer_box.addWidget(self.session_label)
        timer_box.addLayout(ctrl_layout)

        # Update Timer UI Timer
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(200)
        self.update_timer.timeout.connect(self._sync_timer_display)
        self.update_timer.start()

        # Assembly
        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self.canvas)
        layout.addLayout(emotes_layout)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        layout.addSpacing(6)
        layout.addLayout(timer_box)

        self.setLayout(layout)

        # Connect Signals
        if self.room_manager:
            self.room_manager.members_updated.connect(self.on_members_updated)
            self.room_manager.chat_received.connect(self.add_chat_message)
            self.room_manager.room_joined.connect(self.set_room_code)

    def set_room_code(self, code: str):
        self.code_label.setText(f"Room Code: {code}")

    def on_members_updated(self, member_list: list):
        self.canvas.set_members(member_list)

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

    def _sync_timer_display(self):
        """Sync room timer controls display with main_window timer state."""
        mw = self.main_window
        display_seconds = mw.remaining_seconds if mw.timer_mode == "countdown" else mw.elapsed_seconds
        m, s = display_seconds // 60, display_seconds % 60
        self.timer_readout.setText(f"{m:02d}:{s:02d}")

        if mw.current_session == "work":
            self.session_label.setText("FOCUS")
            self.session_label.setStyleSheet(f"color: {self.colors['session_work']}; font-weight: bold;")
        elif mw.current_session == "short_break":
            self.session_label.setText("SHORT BREAK")
            self.session_label.setStyleSheet(f"color: {self.colors['session_short']}; font-weight: bold;")
        else:
            self.session_label.setText("LONG BREAK")
            self.session_label.setStyleSheet(f"color: {self.colors['session_long']}; font-weight: bold;")

        if mw.timer.isActive():
            self.start_btn.setText("Ⅱ")
        else:
            self.start_btn.setText("▶")

    def _toggle_timer(self):
        self.main_window.toggle_timer()

    def _toggle_break(self):
        self.main_window.toggle_break()

    def _reset_timer(self):
        self.main_window.reset_timer()

    def _open_settings(self):
        self.main_window.open_settings()

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
            self.copy_btn.setText("✓ Copied!")
            QGuiApplication.singleShot(2000, lambda: self.copy_btn.setText("📋 Copy Code"))

    def _leave_room(self):
        if self.room_manager:
            self.room_manager.leave_room()
        self.close()

    def closeEvent(self, event):
        """When room window is closed or left, restore the original main window."""
        if self.room_manager:
            self.room_manager.leave_room()
        self.update_timer.stop()
        if self.main_window:
            self.main_window.show()
        super().closeEvent(event)

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

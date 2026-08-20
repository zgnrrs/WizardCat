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
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from wizard_cat.themes import get_theme
from wizard_cat.utils import resource_path


class VirtualRoomCanvas(QWidget):
    """Canvas displaying all connected room members as animated Wizard Cats in a 3x3 grid on a virtual room floor."""

    def __init__(self, parent=None, colors=None):
        super().__init__(parent)
        self.colors = colors or get_theme("wizard_purple")
        self.members: List[dict] = []
        self.reactions: List[dict] = []  # active floating emote bubbles

        self.setMinimumSize(360, 260)

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

        # Fixed 3x3 Grid Seats across Virtual Room Floor (up to 9 wizards)
        count = len(self.members)
        cat_w, cat_h = 65, 65

        col_x = [int(self.width() * 0.22), int(self.width() * 0.50), int(self.width() * 0.78)]
        row_y = [75, 155, 235]

        positions = []
        for i in range(count):
            r = (i // 3) % 3
            c_idx = i % 3
            positions.append((col_x[c_idx], row_y[r]))

        current_frame = self.cat_movie.currentPixmap() if self.cat_movie.isValid() else QPixmap()

        for idx, member in enumerate(self.members):
            if idx >= len(positions):
                break

            cx, cy = positions[idx]
            name = member.get("username", "Wizard")
            lvl = member.get("level", 1)
            status = member.get("status", "FOCUSING")

            # Room session focus stats ONLY (time worked in this active room)
            session_mins = member.get("session_minutes", 0)

            if session_mins < 60:
                stat_time_str = f"{session_mins}m"
            else:
                stat_time_str = f"{session_mins // 60}h {session_mins % 60}m"

            # Shadow under cat
            painter.setBrush(QColor(0, 0, 0, 80))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(cx - 24, cy + cat_h // 2 - 8, 48, 14)

            # Animated Cat Graphic (Animated for all members)
            if not current_frame.isNull():
                painter.drawPixmap(cx - cat_w // 2, cy - cat_h // 2, cat_w, cat_h, current_frame)

            # Floating Personal Room Study Stats Badge Above Cat
            bg_rect = QRectF(cx - 70, cy - cat_h // 2 - 34, 140, 30)
            painter.setBrush(QColor(c["input_bg"]))
            painter.setPen(QColor(c["border"]))
            painter.drawRoundedRect(bg_rect, 6, 6)

            # Username & Level
            painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))
            painter.setPen(QColor(c["accent"]))
            painter.drawText(
                QRectF(cx - 70, cy - cat_h // 2 - 32, 140, 13),
                Qt.AlignmentFlag.AlignCenter,
                f"🧙‍♂️ {name} (Lvl {lvl})",
            )

            # Room Session Time Stat Worked
            status_color = QColor(c["session_work"]) if status == "FOCUSING" else QColor(c["session_long"])
            painter.setPen(status_color)
            painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))

            if status == "FOCUSING":
                personal_stat_str = f"⏱️ Worked: {stat_time_str}"
            else:
                personal_stat_str = f"☕ On Break ({stat_time_str})"

            painter.drawText(
                QRectF(cx - 70, cy - cat_h // 2 - 17, 140, 13),
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

        # Top Bar: Room Code, Copy Code, Shrink (_), Leave Room (🚪)
        self.code_label = QLabel("Room Code: -")

        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.clicked.connect(self._copy_code)

        # Shrink Button (_) placed next to Leave button (like standard window controls)
        self.shrink_btn = QPushButton("_")
        self.shrink_btn.setFixedSize(26, 26)
        self.shrink_btn.setToolTip("Shrink to Mini Floating Timer")
        self.shrink_btn.clicked.connect(self._shrink)

        self.leave_btn = QPushButton("🚪 Leave")
        self.leave_btn.clicked.connect(self._leave_room)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.code_label)
        top_bar.addStretch()
        top_bar.addWidget(self.copy_btn)
        top_bar.addWidget(self.shrink_btn)
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

        # Live Chat Box (Compact spacing without extra blank lines)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFixedHeight(95)
        self.chat_display.document().setDocumentMargin(3)

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

        self.session_label = QLabel("FOCUS")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setFont(main_window.small_font)

        # Pomodoro Timer Progress Bar (Fills parallel with active timer)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setTextVisible(False)

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
        timer_box.addSpacing(2)
        timer_box.addWidget(self.progress_bar)
        timer_box.addSpacing(4)
        timer_box.addLayout(ctrl_layout)

        # Apply Stylesheet
        self._apply_stylesheet()

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
        layout.addSpacing(4)
        layout.addLayout(timer_box)

        self.setLayout(layout)

        # Connect Signals
        if self.room_manager:
            self.room_manager.members_updated.connect(self.on_members_updated)
            self.room_manager.chat_received.connect(self.add_chat_message)
            self.room_manager.room_joined.connect(self.set_room_code)

    def update_theme(self, theme_colors: dict):
        """Update entire room window theme palette live."""
        self.colors = theme_colors
        self.canvas.colors = theme_colors
        self.canvas.update()
        self._apply_stylesheet()
        self._sync_timer_display()

    def set_room_code(self, code: str):
        self.code_label.setText(f"Room Code: {code}")

    def on_members_updated(self, member_list: list):
        self.canvas.set_members(member_list)

    def add_chat_message(self, username: str, text: str, msg_type: str):
        if msg_type == "reaction":
            self.canvas.add_reaction(username, text)
            return

        if msg_type == "system":
            formatted = f"<span style='color: #A0A0A0;'><i><b>system:</b> {username} {text}</i></span>"
        elif msg_type == "level_up":
            formatted = f"<span style='color: #FFD966;'><b>✨ {username}:</b> {text}</span>"
            self.canvas.add_reaction(username, "✨")
        else:
            formatted = f"<b>{username}:</b> {text}"

        self.chat_display.append(formatted)

    def _sync_timer_display(self):
        """Sync room timer controls display and progress bar with main_window timer state."""
        mw = self.main_window
        display_seconds = mw.remaining_seconds if mw.timer_mode == "countdown" else mw.elapsed_seconds
        m, s = display_seconds // 60, display_seconds % 60
        self.timer_readout.setText(f"{m:02d}:{s:02d}")
        self.timer_readout.setStyleSheet(f"color: {self.colors['text_primary']};")

        # Sync Progress Bar in parallel with timer
        if mw.total_seconds > 0:
            if mw.timer_mode == "countdown":
                ratio = max(0.0, min(1.0, (mw.total_seconds - mw.remaining_seconds) / mw.total_seconds))
            else:
                ratio = max(0.0, min(1.0, mw.elapsed_seconds / mw.total_seconds))
        else:
            ratio = 0.0

        self.progress_bar.setValue(int(ratio * 1000))

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

    def _shrink(self):
        if self.main_window:
            self.main_window.shrink_to_mini()

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
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("📋 Copy"))

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
                padding: 2px 4px;
                font-size: 11px;
            }}
            QLineEdit {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 5px;
            }}
            QProgressBar {{
                background-color: {c['input_bg']};
                border: 1px solid {c['border']};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {c['accent']};
                border-radius: 2px;
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
        if hasattr(self, "code_label"):
            self.code_label.setStyleSheet(f"color: {c['accent']}; font-size: 15px; font-weight: bold;")
        if hasattr(self, "shrink_btn"):
            self.shrink_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {c['accent']};
                    border: 1px solid {c['border']};
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {c['accent_hover']};
                    color: {c['text_primary']};
                }}
            """)

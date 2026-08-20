from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QGuiApplication,
    QLinearGradient,
    QPainter,
)
from PySide6.QtWidgets import (
    QDialog,
    QPushButton,
    QSystemTrayIcon,
    QWidget,
)

from wizard_cat.config import load_settings, save_settings
from wizard_cat.room import RoomManager
from wizard_cat.rpg import load_rpg_stats, save_rpg_stats
from wizard_cat.themes import get_theme
from wizard_cat.ui.chat_drawer import RoomChatDrawer, VirtualRoomCanvas
from wizard_cat.ui.room_dialog import RoomDialog
from wizard_cat.ui.settings_dialog import SettingsDialog
from wizard_cat.utils import resource_path


class WizardCat(QWidget):
    """Main desktop widget window for Wizard Cat seamlessly integrating Virtual Room and Pomodoro timer."""

    def __init__(self):
        super().__init__()

        # Window Setup
        self.setWindowTitle("Wizard Cat")
        self.resize(350, 360)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.drag_position = None

        # Load Settings & Theme & RPG Stats
        settings = load_settings()
        self.work_minutes = settings["work_minutes"]
        self.short_break_minutes = settings["short_break_minutes"]
        self.long_break_minutes = settings["long_break_minutes"]
        self.sessions_before_long_break = settings["sessions_before_long_break"]
        self.timer_mode = settings["timer_mode"]
        self.auto_start_breaks = settings["auto_start_breaks"]
        self.auto_start_focus = settings["auto_start_focus"]

        self.theme_key = settings.get("theme", "wizard_purple")
        self.theme = get_theme(self.theme_key)

        self.rpg = load_rpg_stats()

        # Multiplayer Room Manager & Chat Drawer
        self.room_mgr = RoomManager()
        self.chat_drawer = None

        # Font Setup
        font_id = QFontDatabase.addApplicationFont(
            resource_path("fonts/PressStart2P-Regular.ttf")
        )
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.timer_font = QFont(font_family, 24)
            self.small_font = QFont(font_family, 8)
            self.badge_font = QFont(font_family, 7)
        else:
            self.timer_font = QFont("Arial", 30)
            self.small_font = QFont("Arial", 9)
            self.badge_font = QFont("Arial", 8)

        # Session & Minute-by-Minute EXP State
        self.current_session = "work"
        self.completed_sessions = 0
        self.total_seconds = self.work_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.elapsed_seconds = 0
        self.worked_seconds_in_current_minute = 0

        # Embedded Virtual Room Canvas
        self.canvas = VirtualRoomCanvas(self, colors=self.theme)
        self.canvas.setGeometry(10, 28, 330, 180)

        # Connect Room Manager Signals
        self.room_mgr.members_updated.connect(self.on_room_members_updated)
        self.room_mgr.chat_received.connect(self.on_room_chat_received)

        # Timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)

        # UI Controls
        self._init_controls()

        # System Tray
        self.tray_icon = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(
                self.style().standardIcon(
                    self.style().StandardPixmap.SP_ComputerIcon
                )
            )
            self.tray_icon.show()

    def _init_controls(self):
        """Initialize UI control buttons and styling."""
        self.close_button = QPushButton("×", self)
        self.close_button.setGeometry(324, 6, 20, 20)
        self.close_button.clicked.connect(self.close)

        self.settings_button = QPushButton("⚙", self)
        self.settings_button.setGeometry(296, 6, 24, 24)
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.open_settings)

        # Room Button (👥)
        self.room_button = QPushButton("👥", self)
        self.room_button.setGeometry(268, 6, 24, 24)
        self.room_button.setToolTip("Multiplayer Study Room")
        self.room_button.clicked.connect(self.open_room_menu)

        # Chat Button (💬) - Active when in room
        self.chat_button = QPushButton("💬", self)
        self.chat_button.setGeometry(240, 6, 24, 24)
        self.chat_button.setToolTip("Room Chat & Reactions")
        self.chat_button.clicked.connect(self.open_chat_drawer)
        self.chat_button.hide()

        # Copy Room Code Button (📋) - Active when in room
        self.copy_button = QPushButton("📋", self)
        self.copy_button.setGeometry(212, 6, 24, 24)
        self.copy_button.setToolTip("Copy Room Code")
        self.copy_button.clicked.connect(self.copy_room_code)
        self.copy_button.hide()

        # Leave Room Button (🚪) - Active when in room
        self.leave_button = QPushButton("🚪", self)
        self.leave_button.setGeometry(184, 6, 24, 24)
        self.leave_button.setToolTip("Leave Room")
        self.leave_button.clicked.connect(self.leave_room)
        self.leave_button.hide()

        # Bottom Pomodoro Controls
        self.start_button = QPushButton("▶", self)
        self.start_button.setGeometry(133, 290, 42, 32)
        self.start_button.clicked.connect(self.toggle_timer)

        self.break_button = QPushButton("☕", self)
        self.break_button.setGeometry(181, 290, 42, 32)
        self.break_button.clicked.connect(self.toggle_break)

        self.reset_button = QPushButton("↻", self)
        self.reset_button.setGeometry(229, 290, 30, 32)
        self.reset_button.setToolTip("Reset Timer")
        self.reset_button.clicked.connect(self.reset_timer)

        self.update_button_styles()

    def update_button_styles(self):
        """Apply active theme color palette to control buttons."""
        t = self.theme
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {t['accent']};
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{ color: {t['text_primary']}; }}
            QPushButton:pressed {{ color: {t['border']}; }}
        """

        self.close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {t['accent']};
                border: none;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ color: {t['text_primary']}; }}
        """)

        self.settings_button.setStyleSheet(btn_style)
        self.room_button.setStyleSheet(btn_style)
        self.chat_button.setStyleSheet(btn_style)
        self.copy_button.setStyleSheet(btn_style)
        self.leave_button.setStyleSheet(btn_style)

        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['btn_start_bg']};
                color: {t['btn_text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 0px;
                font-size: 17px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {t['btn_start_hover']};
                color: {t['text_primary']};
                border: 1px solid {t['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {t['accent_hover']};
                color: #FFD966;
            }}
        """)

        self.break_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['btn_start_bg']};
                color: {t['text_secondary']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 0px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {t['btn_start_hover']};
                color: {t['text_primary']};
                border: 1px solid {t['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {t['accent_hover']};
                color: #FFD966;
            }}
        """)

        self.reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {t['counter']};
                border: none;
                font-size: 17px;
            }}
            QPushButton:hover {{ color: {t['text_primary']}; }}
        """)

    def on_room_members_updated(self, member_list: list):
        """Update embedded VirtualRoomCanvas when online room members update."""
        self.canvas.set_members(member_list)

    def on_room_chat_received(self, username: str, text: str, msg_type: str):
        """Pass reactions to canvas and chat messages to drawer."""
        if msg_type == "reaction":
            self.canvas.add_reaction(username, text)
        if self.chat_drawer:
            self.chat_drawer.add_chat_message(username, text, msg_type)

    def broadcast_room_presence(self):
        """Immediately broadcast personal study stats and level to active room."""
        if not self.room_mgr or not self.room_mgr.room_code:
            return

        display_seconds = (
            self.remaining_seconds
            if self.timer_mode == "countdown"
            else self.elapsed_seconds
        )
        time_str = f"{display_seconds // 60:02d}:{display_seconds % 60:02d}"
        status = "FOCUSING" if self.current_session == "work" else "ON BREAK"

        if self.timer_mode == "countdown":
            session_mins = (self.total_seconds - self.remaining_seconds) // 60
        else:
            session_mins = self.elapsed_seconds // 60

        self.room_mgr.broadcast_presence(
            level=self.rpg.level,
            title=self.rpg.title,
            status=status,
            time_str=time_str,
            total_focus_minutes=self.rpg.total_focus_minutes,
            session_minutes=max(0, session_mins),
        )

    def open_room_menu(self):
        """Open multiplayer room creation/joining dialog."""
        dialog = RoomDialog(self, default_username=self.room_mgr.username)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.action == "create":
                code = self.room_mgr.generate_room_code()
                joined = self.room_mgr.connect_and_join(code, dialog.username)
            elif dialog.action == "join":
                joined = self.room_mgr.connect_and_join(dialog.room_code, dialog.username)
            else:
                joined = False

            if joined:
                self.chat_button.show()
                self.copy_button.show()
                self.leave_button.show()
                self.broadcast_room_presence()

    def open_chat_drawer(self):
        """Open or raise pop-over chat drawer."""
        if not self.chat_drawer:
            self.chat_drawer = RoomChatDrawer(self, self.room_mgr)
        self.chat_drawer.show()
        self.chat_drawer.raise_()
        self.chat_drawer.activateWindow()

    def copy_room_code(self):
        """Copy active room code to clipboard."""
        if self.room_mgr and self.room_mgr.room_code:
            QGuiApplication.clipboard().setText(self.room_mgr.room_code)
            self.show_notification("Room Code Copied!", f"Code {self.room_mgr.room_code} copied to clipboard.")

    def leave_room(self):
        """Leave current online room and switch back to solo cat mode."""
        if self.room_mgr:
            self.room_mgr.leave_room()
        self.chat_button.hide()
        self.copy_button.hide()
        self.leave_button.hide()
        if self.chat_drawer:
            self.chat_drawer.close()
            self.chat_drawer = None
        self.canvas.set_members([])

    def open_settings(self):
        """Open settings dialog and apply updated preferences and theme."""
        was_running = self.timer.isActive()
        if was_running:
            self.timer.stop()

        dialog = SettingsDialog(self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.work_minutes = dialog.work_spin.value()
            self.short_break_minutes = dialog.short_break_spin.value()
            self.long_break_minutes = dialog.long_break_spin.value()
            self.sessions_before_long_break = dialog.sessions_spin.value()
            self.timer_mode = dialog.mode_combo.currentData()
            self.auto_start_breaks = dialog.auto_break_checkbox.isChecked()
            self.auto_start_focus = dialog.auto_focus_checkbox.isChecked()

            self.theme_key = dialog.theme_combo.currentData()
            self.theme = get_theme(self.theme_key)
            self.canvas.colors = self.theme
            self.canvas.update()
            self.update_button_styles()

            save_settings({
                "work_minutes": self.work_minutes,
                "short_break_minutes": self.short_break_minutes,
                "long_break_minutes": self.long_break_minutes,
                "sessions_before_long_break": self.sessions_before_long_break,
                "timer_mode": self.timer_mode,
                "auto_start_breaks": self.auto_start_breaks,
                "auto_start_focus": self.auto_start_focus,
                "theme": self.theme_key,
            })

            self.reset_current_session()

        if was_running:
            self.timer.start()

        self.setFocus()

    def reset_current_session(self):
        """Reset seconds count for current session type."""
        if self.current_session == "work":
            minutes = self.work_minutes
        elif self.current_session == "short_break":
            minutes = self.short_break_minutes
        else:
            minutes = self.long_break_minutes

        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds
        self.elapsed_seconds = 0
        self.worked_seconds_in_current_minute = 0
        self.broadcast_room_presence()
        self.update()

    def reset_timer(self):
        """Stop and reset timer back to initial session state."""
        self.timer.stop()
        self.remaining_seconds = self.total_seconds
        self.elapsed_seconds = 0
        self.worked_seconds_in_current_minute = 0
        self.start_button.setText("▶")
        self.broadcast_room_presence()
        self.update()
        self.setFocus()

    def update_timer(self):
        """Timer tick handler called every second with minute-by-minute EXP calculation and room presence."""
        # Award 2 EXP for every 60 seconds worked in focus mode
        if self.current_session == "work":
            self.worked_seconds_in_current_minute += 1
            if self.worked_seconds_in_current_minute >= 60:
                self.worked_seconds_in_current_minute = 0
                leveled_up, new_level, new_title = self.rpg.add_exp(
                    2, focus_minutes=1
                )
                save_rpg_stats(self.rpg)
                if leveled_up:
                    self.show_notification(
                        f"✨ LEVEL UP! (Lvl {new_level})",
                        f"Congratulations! Your new title: {new_title} 🪄",
                    )
                    self.room_mgr.announce_level_up(new_level, new_title)

        if self.timer_mode == "countdown":
            if self.remaining_seconds > 0:
                self.remaining_seconds -= 1
            else:
                self.finish_session()
        else:
            self.elapsed_seconds += 1
            if self.elapsed_seconds >= self.total_seconds:
                self.finish_session()

        # Broadcast presence heartbeat to room
        self.broadcast_room_presence()
        self.update()

    def finish_session(self):
        """Handle session completion state transitions and notifications."""
        self.timer.stop()
        self.worked_seconds_in_current_minute = 0

        if self.current_session == "work":
            self.completed_sessions += 1
            self.show_notification(
                "Focus Session Completed! ✨",
                "Time for a break.",
            )

            if self.completed_sessions % self.sessions_before_long_break == 0:
                self.current_session = "long_break"
            else:
                self.current_session = "short_break"

            self.reset_current_session()
            self.start_button.setText("▶")

            if self.auto_start_breaks:
                self.timer.start()
                self.start_button.setText("Ⅱ")

        else:
            self.show_notification("Break Over! 🪄", "Time for a new focus session.")
            self.current_session = "work"
            self.reset_current_session()
            self.start_button.setText("▶")

            if self.auto_start_focus:
                self.timer.start()
                self.start_button.setText("Ⅱ")

        self.broadcast_room_presence()
        self.update()

    def toggle_timer(self):
        """Start or pause the timer."""
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setText("▶")
        else:
            self.timer.start()
            self.start_button.setText("Ⅱ")

        self.broadcast_room_presence()
        self.setFocus()

    def toggle_break(self):
        """Switch manually between focus and break sessions."""
        self.timer.stop()

        if self.current_session == "work":
            self.current_session = "short_break"
        else:
            self.current_session = "work"

        self.reset_current_session()
        self.start_button.setText("▶")
        self.broadcast_room_presence()
        self.update()
        self.setFocus()

    def show_notification(self, title: str, message: str):
        """Display desktop notification using system tray."""
        if self.tray_icon and QSystemTrayIcon.supportsMessages():
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                4000,
            )

    def paintEvent(self, event):
        """Custom painter for background gradient, stars, RPG stats, and Pomodoro controls."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = self.theme

        # Background Gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(t["bg_gradient"][0]))
        gradient.setColorAt(0.55, QColor(t["bg_gradient"][1]))
        gradient.setColorAt(1.0, QColor(t["bg_gradient"][2]))

        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 18, 18)

        # Stars
        stars = [
            (35, 35, 2),
            (82, 22, 1),
            (125, 48, 2),
            (175, 28, 1),
            (225, 45, 2),
            (270, 30, 1),
            (300, 60, 2),
            (55, 75, 1),
            (145, 75, 1),
            (250, 85, 1),
        ]
        for x, y, size in stars:
            painter.setBrush(QColor(t["stars"]))
            painter.drawRect(x, y, size, size)

        # RPG Level & Title Badge (Top Left) or Room Code
        painter.setFont(self.badge_font)
        painter.setPen(QColor(t["badge"]))
        if self.room_mgr.room_code:
            top_badge_text = f"Room: {self.room_mgr.room_code} • Lvl {self.rpg.level}"
        else:
            top_badge_text = f"✦ Lvl {self.rpg.level} • {self.rpg.title}"

        painter.drawText(
            12,
            6,
            170,
            24,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            top_badge_text,
        )

        # Timer Text
        painter.setFont(self.timer_font)
        painter.setPen(QColor(t["text_primary"]))

        display_seconds = (
            self.remaining_seconds
            if self.timer_mode == "countdown"
            else self.elapsed_seconds
        )
        minutes = display_seconds // 60
        seconds = display_seconds % 60
        time_text = f"{minutes:02d}:{seconds:02d}"

        painter.drawText(
            0,
            215,
            self.width(),
            36,
            Qt.AlignmentFlag.AlignCenter,
            time_text,
        )

        # Session Label Text
        painter.setFont(self.small_font)
        if self.current_session == "work":
            session_text = "FOCUS"
            session_color = QColor(t["session_work"])
        elif self.current_session == "short_break":
            session_text = "SHORT BREAK"
            session_color = QColor(t["session_short"])
        else:
            session_text = "LONG BREAK"
            session_color = QColor(t["session_long"])

        painter.setPen(session_color)
        painter.drawText(
            0,
            253,
            self.width(),
            16,
            Qt.AlignmentFlag.AlignCenter,
            session_text,
        )

        # EXP Progress Bar (Above Control Buttons)
        exp_bar_x = 45
        exp_bar_y = 276
        exp_bar_w = 260
        exp_bar_h = 5

        # Background track
        painter.setBrush(QColor(t["input_bg"]))
        painter.setPen(QColor(t["border"]))
        painter.drawRoundedRect(exp_bar_x, exp_bar_y, exp_bar_w, exp_bar_h, 2, 2)

        # Filled progress
        fill_ratio = min(1.0, self.rpg.exp / self.rpg.required_exp)
        if fill_ratio > 0:
            fill_w = max(4, int(exp_bar_w * fill_ratio))
            exp_gradient = QLinearGradient(exp_bar_x, 0, exp_bar_x + fill_w, 0)
            exp_gradient.setColorAt(0.0, QColor(t["exp_bar_gradient"][0]))
            exp_gradient.setColorAt(1.0, QColor(t["exp_bar_gradient"][1]))
            painter.setBrush(exp_gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(exp_bar_x, exp_bar_y, fill_w, exp_bar_h, 2, 2)

        # Bottom Bar: Pomodoro Counter (Left) & EXP Counter (Right)
        painter.setFont(QFont(self.small_font.family(), 7))
        painter.setPen(QColor(t["counter"]))

        counter_text = (
            f"{self.completed_sessions} / {self.sessions_before_long_break}"
        )
        painter.drawText(
            15,
            338,
            80,
            12,
            Qt.AlignmentFlag.AlignLeft,
            counter_text,
        )

        exp_text = f"{self.rpg.exp}/{self.rpg.required_exp} EXP"
        painter.drawText(
            225,
            338,
            110,
            12,
            Qt.AlignmentFlag.AlignRight,
            exp_text,
        )

    def keyPressEvent(self, event):
        """Keyboard shortcut handler for Space (start/pause) and R (reset)."""
        if event.key() == Qt.Key.Key_Space:
            self.toggle_timer()
            return
        if event.key() == Qt.Key.Key_R:
            self.reset_timer()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Window drag start handler."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        """Window dragging motion handler."""
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and self.drag_position is not None
        ):
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event):
        """Window drag release handler."""
        self.drag_position = None

    def closeEvent(self, event):
        """Cleanly leave active study room when window closes."""
        if self.room_mgr:
            self.room_mgr.leave_room()
        super().closeEvent(event)

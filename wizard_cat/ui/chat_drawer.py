from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from wizard_cat.themes import get_theme


class RoomPanel(QDialog):
    """Pop-out window displaying active room members, live status, and room chat."""

    def __init__(self, parent=None, room_manager=None):
        super().__init__(parent)
        self.room_manager = room_manager
        self.setWindowTitle("Wizard Cat - Oda & Sohbet")
        self.setFixedSize(360, 480)

        theme_key = getattr(parent, "theme_key", "wizard_purple")
        self.colors = get_theme(theme_key)
        self._apply_stylesheet()

        # Room Code Header
        self.code_label = QLabel("Oda Kodu: -")
        self.code_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['accent']};
                font-size: 15px;
                font-weight: bold;
            }}
        """)

        self.copy_btn = QPushButton("📋 Kodu Kopyala")
        self.copy_btn.clicked.connect(self._copy_code)

        self.leave_btn = QPushButton("🚪 Odadan Ayrıl")
        self.leave_btn.clicked.connect(self._leave_room)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.code_label)
        top_bar.addStretch()
        top_bar.addWidget(self.copy_btn)
        top_bar.addWidget(self.leave_btn)

        # Members List Section
        members_title = QLabel("👥 Odadaki Büyücüler:")
        members_title.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.members_list = QListWidget()
        self.members_list.setFixedHeight(120)

        # Chat Section
        chat_title = QLabel("💬 Oda Sohbeti:")
        chat_title.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Mesajınızı yazın...")
        self.chat_input.returnPressed.connect(self._send_chat)

        send_btn = QPushButton("Gönder")
        send_btn.clicked.connect(self._send_chat)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)

        # Layout Assembly
        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addSpacing(6)
        layout.addWidget(members_title)
        layout.addWidget(self.members_list)
        layout.addSpacing(6)
        layout.addWidget(chat_title)
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        self.setLayout(layout)

        # Connect Room Signals
        if self.room_manager:
            self.room_manager.members_updated.connect(self.update_members)
            self.room_manager.chat_received.connect(self.add_chat_message)
            self.room_manager.room_joined.connect(self.set_room_code)

    def set_room_code(self, code: str):
        self.code_label.setText(f"Oda Kodu: {code}")

    def update_members(self, member_list: list):
        self.members_list.clear()
        for m in member_list:
            name = m.get("username", "Wizard")
            lvl = m.get("level", 1)
            title = m.get("title", "")
            status = m.get("status", "FOCUSING")
            t_str = m.get("time_str", "")

            item_text = f"🧙‍♂️ {name}  (Lvl {lvl} • {title})\n     └ Status: {status} [{t_str}]"
            item = QListWidgetItem(item_text)
            self.members_list.addItem(item)

    def add_chat_message(self, username: str, text: str, msg_type: str):
        if msg_type == "system":
            formatted = f"<i><b>system:</b> {username} {text}</i><br>"
        elif msg_type == "level_up":
            formatted = f"<b style='color: #FFD966;'>✨ {username}:</b> {text}<br>"
        else:
            formatted = f"<b>{username}:</b> {text}<br>"
        self.chat_display.append(formatted)

    def _send_chat(self):
        txt = self.chat_input.text().strip()
        if txt and self.room_manager:
            self.room_manager.send_chat_message(txt)
            self.chat_input.clear()

    def _copy_code(self):
        if self.room_manager and self.room_manager.room_code:
            QGuiApplication.clipboard().setText(self.room_manager.room_code)
            self.copy_btn.setText("✓ Kopyalandı!")
            QGuiApplication.singleShot(2000, lambda: self.copy_btn.setText("📋 Kodu Kopyala"))

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
            QListWidget, QTextEdit {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px;
            }}
            QLineEdit {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px;
            }}
            QPushButton {{
                background-color: {c['dialog_bg']};
                color: {c['text_secondary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 5px 8px;
            }}
            QPushButton:hover {{
                background-color: {c['accent_hover']};
                border: 1px solid {c['border_hover']};
                color: {c['text_primary']};
            }}
        """)

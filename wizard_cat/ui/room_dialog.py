from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from wizard_cat.themes import get_theme


class RoomDialog(QDialog):
    """Modal dialog for creating or joining a multiplayer study room."""

    def __init__(self, parent=None, default_username="WizardCat"):
        super().__init__(parent)
        self.setWindowTitle("Birlikte Çalışma Odası (Multiplayer)")
        self.setFixedSize(340, 290)

        theme_key = getattr(parent, "theme_key", "wizard_purple")
        self.colors = get_theme(theme_key)
        self._apply_stylesheet()

        self.action = None  # "create" or "join"
        self.username = default_username
        self.room_code = ""

        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setText(default_username)
        self.username_input.setPlaceholderText("Büyücü adınız...")

        self.room_code_input = QLineEdit()
        self.room_code_input.setPlaceholderText("Örn: CAT-4029")

        # Layout
        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Kullanıcı Adı:", self.username_input)
        form.addRow("Oda Kodu (Katıl):", self.room_code_input)

        # Buttons
        create_btn = QPushButton("✨ Yeni Oda Oluştur")
        create_btn.clicked.connect(self._on_create)

        join_btn = QPushButton("🚀 Odaya Katıl")
        join_btn.clicked.connect(self._on_join)

        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(join_btn)

        layout = QVBoxLayout()
        title = QLabel("👥  Birlikte Çalışma Odası")
        title.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['accent']};
                font-size: 16px;
                font-weight: bold;
            }}
        """)

        subtitle = QLabel("Arkadaşlarınızla aynı oda kodunu paylaşarak birlikte çalışın ve sohbet edin!")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 11px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addLayout(form)
        layout.addSpacing(10)
        layout.addWidget(create_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _on_create(self):
        self.action = "create"
        self.username = self.username_input.text().strip() or "WizardCat"
        self.accept()

    def _on_join(self):
        code = self.room_code_input.text().strip().upper()
        if not code:
            self.room_code_input.setFocus()
            return

        self.action = "join"
        self.username = self.username_input.text().strip() or "WizardCat"
        self.room_code = code
        self.accept()

    def _apply_stylesheet(self):
        c = self.colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c['dialog_bg']};
                color: {c['text_secondary']};
            }}
            QLabel {{ color: {c['text_secondary']}; }}
            QLineEdit {{
                background-color: {c['input_bg']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px;
            }}
            QLineEdit:focus {{ border: 1px solid {c['border_hover']}; }}
            QPushButton {{
                background-color: {c['dialog_bg']};
                color: {c['text_secondary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 7px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {c['accent_hover']};
                border: 1px solid {c['border_hover']};
                color: {c['text_primary']};
            }}
        """)

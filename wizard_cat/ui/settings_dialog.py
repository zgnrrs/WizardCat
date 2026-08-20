from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from wizard_cat.themes import get_all_themes, get_theme


class SettingsDialog(QDialog):
    """Modal dialog for customizing Pomodoro timer settings and color theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wizard Cat - Settings")
        self.setFixedSize(330, 430)

        # Get parent theme colors
        current_theme_key = getattr(parent, "theme_key", "wizard_purple")
        theme_colors = get_theme(current_theme_key)

        self._apply_stylesheet(theme_colors)

        # Work / Break Durations
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 180)
        self.work_spin.setSuffix(" dk")
        self.work_spin.setValue(parent.work_minutes if parent else 25)

        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 60)
        self.short_break_spin.setSuffix(" dk")
        self.short_break_spin.setValue(parent.short_break_minutes if parent else 5)

        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 120)
        self.long_break_spin.setSuffix(" dk")
        self.long_break_spin.setValue(parent.long_break_minutes if parent else 15)

        self.sessions_spin = QSpinBox()
        self.sessions_spin.setRange(1, 20)
        self.sessions_spin.setSuffix(" pomodoro")
        self.sessions_spin.setValue(parent.sessions_before_long_break if parent else 4)

        # Timer Mode
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Geri sayım", "countdown")
        self.mode_combo.addItem("İleri sayım", "countup")
        if parent and parent.timer_mode == "countdown":
            self.mode_combo.setCurrentIndex(0)
        else:
            self.mode_combo.setCurrentIndex(1)

        # Theme Selector
        self.theme_combo = QComboBox()
        themes = get_all_themes()
        selected_index = 0
        for idx, (t_key, t_name) in enumerate(themes.items()):
            self.theme_combo.addItem(t_name, t_key)
            if t_key == current_theme_key:
                selected_index = idx
        self.theme_combo.setCurrentIndex(selected_index)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

        # Auto Transitions
        self.auto_break_checkbox = QCheckBox("Molaları otomatik başlat")
        self.auto_break_checkbox.setChecked(parent.auto_start_breaks if parent else True)

        self.auto_focus_checkbox = QCheckBox("Moladan sonra çalışmayı otomatik başlat")
        self.auto_focus_checkbox.setChecked(parent.auto_start_focus if parent else False)

        # Form Layout
        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Çalışma süresi:", self.work_spin)
        form.addRow("Kısa mola:", self.short_break_spin)
        form.addRow("Uzun mola:", self.long_break_spin)
        form.addRow("Uzun mola aralığı:", self.sessions_spin)
        form.addRow("Sayaç modu:", self.mode_combo)
        form.addRow("Renk Teması:", self.theme_combo)

        # Buttons
        save_button = QPushButton("Kaydet")
        cancel_button = QPushButton("İptal")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)

        # Main Layout
        layout = QVBoxLayout()
        self.title_label = QLabel("✦  Wizard Cat Ayarları")
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_colors['accent']};
                font-size: 17px;
                font-weight: bold;
            }}
        """)

        layout.addWidget(self.title_label)
        layout.addSpacing(10)
        layout.addLayout(form)
        layout.addSpacing(10)
        layout.addWidget(self.auto_break_checkbox)
        layout.addWidget(self.auto_focus_checkbox)
        layout.addStretch()
        layout.addLayout(buttons)

        self.setLayout(layout)

    def _on_theme_changed(self):
        """Update settings dialog stylesheet live when user changes theme dropdown."""
        theme_key = self.theme_combo.currentData()
        theme_colors = get_theme(theme_key)
        self._apply_stylesheet(theme_colors)
        if hasattr(self, "title_label"):
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme_colors['accent']};
                    font-size: 17px;
                    font-weight: bold;
                }}
            """)

    def _apply_stylesheet(self, colors: dict):
        """Apply dynamic stylesheet based on theme color palette."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['dialog_bg']};
                color: {colors['text_secondary']};
            }}

            QLabel {{
                color: {colors['text_secondary']};
                font-size: 12px;
            }}

            QSpinBox, QComboBox {{
                background-color: {colors['input_bg']};
                color: {colors['text_secondary']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 6px;
            }}

            QSpinBox:hover, QComboBox:hover {{
                border: 1px solid {colors['border_hover']};
            }}

            QCheckBox {{
                color: {colors['text_secondary']};
                spacing: 8px;
            }}

            QPushButton {{
                background-color: {colors['dialog_bg']};
                color: {colors['text_secondary']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 7px;
            }}

            QPushButton:hover {{
                background-color: {colors['accent_hover']};
                border: 1px solid {colors['border_hover']};
            }}
        """)

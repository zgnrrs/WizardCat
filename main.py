import sys
import json
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(
        base_path,
        relative_path
    )


from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QDialog,
    QLabel,
    QSpinBox,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QCheckBox,
    QSystemTrayIcon
)

from PySide6.QtCore import (
    Qt,
    QTimer
)

from PySide6.QtGui import (
    QPainter,
    QColor,
    QLinearGradient,
    QFont,
    QFontDatabase,
    QMovie
)


# ======================================================
# AYARLAR
# ======================================================

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_before_long_break": 4,
    "timer_mode": "countdown",
    "auto_start_breaks": True,
    "auto_start_focus": False
}


def load_settings():

    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)

        return settings

    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):

    try:
        with open(
            SETTINGS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                settings,
                file,
                indent=4,
                ensure_ascii=False
            )

    except Exception as error:

        print(
            "Ayarlar kaydedilemedi:",
            error
        )


# ======================================================
# AYARLAR PENCERESİ
# ======================================================

class SettingsDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "Wizard Cat - Settings"
        )

        self.setFixedSize(
            330,
            390
        )

        self.setStyleSheet("""
            QDialog {
                background-color: #17113B;
                color: #E8DFFF;
            }

            QLabel {
                color: #E8DFFF;
                font-size: 12px;
            }

            QSpinBox,
            QComboBox {
                background-color: #0B0924;
                color: #E8DFFF;
                border: 1px solid #6D4BA8;
                border-radius: 6px;
                padding: 6px;
            }

            QSpinBox:hover,
            QComboBox:hover {
                border: 1px solid #A875FF;
            }

            QCheckBox {
                color: #E8DFFF;
                spacing: 8px;
            }

            QPushButton {
                background-color: #32175C;
                color: #E8DFFF;
                border: 1px solid #6D4BA8;
                border-radius: 6px;
                padding: 7px;
            }

            QPushButton:hover {
                background-color: #4A2878;
                border: 1px solid #A875FF;
            }
        """)

        # --------------------------------------------------
        # SÜRELER
        # --------------------------------------------------

        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 180)
        self.work_spin.setSuffix(" dk")
        self.work_spin.setValue(
            parent.work_minutes
        )

        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 60)
        self.short_break_spin.setSuffix(" dk")
        self.short_break_spin.setValue(
            parent.short_break_minutes
        )

        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 120)
        self.long_break_spin.setSuffix(" dk")
        self.long_break_spin.setValue(
            parent.long_break_minutes
        )

        self.sessions_spin = QSpinBox()
        self.sessions_spin.setRange(1, 20)
        self.sessions_spin.setSuffix(" pomodoro")
        self.sessions_spin.setValue(
            parent.sessions_before_long_break
        )

        # --------------------------------------------------
        # SAYAÇ MODU
        # --------------------------------------------------

        self.mode_combo = QComboBox()

        self.mode_combo.addItem(
            "Geri sayım",
            "countdown"
        )

        self.mode_combo.addItem(
            "İleri sayım",
            "countup"
        )

        if parent.timer_mode == "countdown":

            self.mode_combo.setCurrentIndex(0)

        else:

            self.mode_combo.setCurrentIndex(1)

        # --------------------------------------------------
        # OTOMATİK GEÇİŞLER
        # --------------------------------------------------

        self.auto_break_checkbox = QCheckBox(
            "Molaları otomatik başlat"
        )

        self.auto_break_checkbox.setChecked(
            parent.auto_start_breaks
        )

        self.auto_focus_checkbox = QCheckBox(
            "Moladan sonra çalışmayı otomatik başlat"
        )

        self.auto_focus_checkbox.setChecked(
            parent.auto_start_focus
        )

        # --------------------------------------------------
        # FORM
        # --------------------------------------------------

        form = QFormLayout()

        form.setSpacing(12)

        form.addRow(
            "Çalışma süresi:",
            self.work_spin
        )

        form.addRow(
            "Kısa mola:",
            self.short_break_spin
        )

        form.addRow(
            "Uzun mola:",
            self.long_break_spin
        )

        form.addRow(
            "Uzun mola aralığı:",
            self.sessions_spin
        )

        form.addRow(
            "Sayaç modu:",
            self.mode_combo
        )

        # --------------------------------------------------
        # BUTONLAR
        # --------------------------------------------------

        save_button = QPushButton(
            "Kaydet"
        )

        cancel_button = QPushButton(
            "İptal"
        )

        save_button.clicked.connect(
            self.accept
        )

        cancel_button.clicked.connect(
            self.reject
        )

        buttons = QHBoxLayout()

        buttons.addWidget(
            cancel_button
        )

        buttons.addWidget(
            save_button
        )

        # --------------------------------------------------
        # ANA LAYOUT
        # --------------------------------------------------

        layout = QVBoxLayout()

        title = QLabel(
            "✦  Wizard Cat Ayarları"
        )

        title.setStyleSheet("""
            QLabel {
                color: #C89BFF;
                font-size: 17px;
                font-weight: bold;
            }
        """)

        layout.addWidget(title)

        layout.addSpacing(12)

        layout.addLayout(form)

        layout.addSpacing(12)

        layout.addWidget(
            self.auto_break_checkbox
        )

        layout.addWidget(
            self.auto_focus_checkbox
        )

        layout.addStretch()

        layout.addLayout(buttons)

        self.setLayout(layout)


# ======================================================
# ANA WIZARD CAT
# ======================================================

class WizardCat(QWidget):

    def __init__(self):

        super().__init__()

        # ==================================================
        # PENCERE
        # ==================================================

        self.setWindowTitle(
            "Wizard Cat"
        )

        # Biraz daha ferah pencere
        self.resize(
            320,
            250
        )

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
        )

        self.drag_position = None

        # ==================================================
        # AYARLAR
        # ==================================================

        settings = load_settings()

        self.work_minutes = settings[
            "work_minutes"
        ]

        self.short_break_minutes = settings[
            "short_break_minutes"
        ]

        self.long_break_minutes = settings[
            "long_break_minutes"
        ]

        self.sessions_before_long_break = settings[
            "sessions_before_long_break"
        ]

        self.timer_mode = settings[
            "timer_mode"
        ]

        self.auto_start_breaks = settings[
            "auto_start_breaks"
        ]

        self.auto_start_focus = settings[
            "auto_start_focus"
        ]

        # ==================================================
        # FONT
        # ==================================================

        font_id = QFontDatabase.addApplicationFont(
    resource_path(
        "fonts/PressStart2P-Regular.ttf"
    )
)

        if font_id != -1:

            font_family = (
                QFontDatabase
                .applicationFontFamilies(
                    font_id
                )[0]
            )

            self.timer_font = QFont(
                font_family,
                24
            )

            self.small_font = QFont(
                font_family,
                8
            )

        else:

            self.timer_font = QFont(
                "Arial",
                32
            )

            self.small_font = QFont(
                "Arial",
                9
            )

        # ==================================================
        # OTURUM
        # ==================================================

        self.current_session = "work"

        self.completed_sessions = 0

        self.total_seconds = (
            self.work_minutes * 60
        )

        self.remaining_seconds = (
            self.total_seconds
        )

        self.elapsed_seconds = 0

        # ==================================================
        # TIMER
        # ==================================================

        self.timer = QTimer(self)

        self.timer.setInterval(1000)

        self.timer.timeout.connect(
            self.update_timer
        )

        # ==================================================
        # KEDİ
        # ==================================================

        self.cat_movie = QMovie(
    resource_path(
        "assets/cat/wizard_cat.gif"
    )
)

        self.cat_movie.setCacheMode(
            QMovie.CacheMode.CacheAll
        )

        self.cat_movie.frameChanged.connect(
            self.update
        )

        self.cat_movie.start()

        # ==================================================
        # KAPATMA BUTONU
        # ==================================================

        self.close_button = QPushButton(
            "×",
            self
        )

        self.close_button.setGeometry(
            294,
            8,
            20,
            20
        )

        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #B99AEF;
                border: none;
                padding: 0px;
                margin: 0px;
                font-size: 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                color: #E8DFFF;
            }

            QPushButton:pressed {
                color: #8B65D1;
            }
        """)

        self.close_button.clicked.connect(
            self.close
        )

        # ==================================================
        # AYARLAR BUTONU
        # ==================================================

        self.settings_button = QPushButton(
            "⚙",
            self
        )

        self.settings_button.setGeometry(
            266,
            8,
            24,
            24
        )

        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #B99AEF;
                border: none;
                font-size: 15px;
            }

            QPushButton:hover {
                color: #E8DFFF;
            }

            QPushButton:pressed {
                color: #8B65D1;
            }
        """)

        self.settings_button.clicked.connect(
            self.open_settings
        )

        # ==================================================
        # BAŞLAT / DURDUR
        # ==================================================

        self.start_button = QPushButton(
            "▶",
            self
        )

        self.start_button.setGeometry(
            118,
            207,
            40,
            32
        )

        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(11, 9, 36, 150);
                color: #C89BFF;
                border: 1px solid #6D4BA8;
                border-radius: 6px;
                padding: 0px;
                font-size: 17px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: rgba(50, 30, 92, 190);
                color: #E8DFFF;
                border: 1px solid #A875FF;
            }

            QPushButton:pressed {
                background-color: rgba(40, 20, 75, 220);
                color: #FFD966;
            }
        """)

        self.start_button.clicked.connect(
            self.toggle_timer
        )

        # ==================================================
        # KAHVE / MOLA
        # ==================================================

        self.break_button = QPushButton(
            "☕",
            self
        )

        self.break_button.setGeometry(
            164,
            207,
            40,
            32
        )

        self.break_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(11, 9, 36, 150);
                color: #D7B8FF;
                border: 1px solid #6D4BA8;
                border-radius: 6px;
                padding: 0px;
                font-size: 15px;
            }

            QPushButton:hover {
                background-color: rgba(50, 30, 92, 190);
                color: #FFE6A3;
                border: 1px solid #A875FF;
            }

            QPushButton:pressed {
                background-color: rgba(40, 20, 75, 220);
                color: #FFD966;
            }
        """)

        self.break_button.clicked.connect(
            self.toggle_break
        )

        # ==================================================
        # RESET
        # ==================================================

        self.reset_button = QPushButton(
            "↻",
            self
        )

        self.reset_button.setGeometry(
            210,
            207,
            30,
            32
        )

        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #9D83C7;
                border: none;
                font-size: 17px;
            }

            QPushButton:hover {
                color: #E8DFFF;
            }
        """)

        self.reset_button.clicked.connect(
            self.reset_timer
        )

        # ==================================================
        # SYSTEM TRAY
        # ==================================================

        self.tray_icon = None

        if QSystemTrayIcon.isSystemTrayAvailable():

            self.tray_icon = QSystemTrayIcon(
                self
            )

            self.tray_icon.setIcon(
                self.style().standardIcon(
                    self.style().StandardPixmap.SP_ComputerIcon
                )
            )

            self.tray_icon.show()

    # ======================================================
    # AYARLAR
    # ======================================================

    def open_settings(self):

        was_running = (
            self.timer.isActive()
        )

        if was_running:

            self.timer.stop()
            self.cat_movie.stop()

        dialog = SettingsDialog(self)

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:

            self.work_minutes = (
                dialog.work_spin.value()
            )

            self.short_break_minutes = (
                dialog.short_break_spin.value()
            )

            self.long_break_minutes = (
                dialog.long_break_spin.value()
            )

            self.sessions_before_long_break = (
                dialog.sessions_spin.value()
            )

            self.timer_mode = (
                dialog.mode_combo.currentData()
            )

            self.auto_start_breaks = (
                dialog.auto_break_checkbox.isChecked()
            )

            self.auto_start_focus = (
                dialog.auto_focus_checkbox.isChecked()
            )

            save_settings({
                "work_minutes":
                    self.work_minutes,

                "short_break_minutes":
                    self.short_break_minutes,

                "long_break_minutes":
                    self.long_break_minutes,

                "sessions_before_long_break":
                    self.sessions_before_long_break,

                "timer_mode":
                    self.timer_mode,

                "auto_start_breaks":
                    self.auto_start_breaks,

                "auto_start_focus":
                    self.auto_start_focus
            })

            self.reset_current_session()

        if was_running:

            self.timer.start()
            self.cat_movie.start()

        self.setFocus()

    # ======================================================
    # OTURUMU SIFIRLA
    # ======================================================

    def reset_current_session(self):

        if self.current_session == "work":

            minutes = self.work_minutes

        elif self.current_session == "short_break":

            minutes = self.short_break_minutes

        else:

            minutes = self.long_break_minutes

        self.total_seconds = (
            minutes * 60
        )

        self.remaining_seconds = (
            self.total_seconds
        )

        self.elapsed_seconds = 0

        self.update()

    # ======================================================
    # TIMER RESET
    # ======================================================

    def reset_timer(self):

        self.timer.stop()
        self.cat_movie.stop()

        self.remaining_seconds = (
            self.total_seconds
        )

        self.elapsed_seconds = 0

        self.start_button.setText(
            "▶"
        )

        self.update()

        self.setFocus()

    # ======================================================
    # TIMER
    # ======================================================

    def update_timer(self):

        if self.timer_mode == "countdown":

            if self.remaining_seconds > 0:

                self.remaining_seconds -= 1

            else:

                self.finish_session()

        else:

            self.elapsed_seconds += 1

            if self.elapsed_seconds >= self.total_seconds:

                self.finish_session()

        self.update()

    # ======================================================
    # OTURUM BİTTİ
    # ======================================================

    def finish_session(self):

        self.timer.stop()
        self.cat_movie.stop()

        if self.current_session == "work":

            self.completed_sessions += 1

            self.show_notification(
                "Focus tamamlandı! ✨",
                "Biraz dinlenme zamanı."
            )

            if (
                self.completed_sessions
                % self.sessions_before_long_break
                == 0
            ):

                self.current_session = (
                    "long_break"
                )

            else:

                self.current_session = (
                    "short_break"
                )

            self.reset_current_session()

            self.start_button.setText(
                "▶"
            )

            if self.auto_start_breaks:

                self.timer.start()
                self.cat_movie.start()

                self.start_button.setText(
                    "Ⅱ"
                )

        else:

            self.show_notification(
                "Mola bitti! 🪄",
                "Yeni bir focus zamanı."
            )

            self.current_session = "work"

            self.reset_current_session()

            self.start_button.setText(
                "▶"
            )

            if self.auto_start_focus:

                self.timer.start()
                self.cat_movie.start()

                self.start_button.setText(
                    "Ⅱ"
                )

        self.update()

    # ======================================================
    # BAŞLAT / DURDUR
    # ======================================================

    def toggle_timer(self):

        if self.timer.isActive():

            self.timer.stop()
            self.cat_movie.stop()

            self.start_button.setText(
                "▶"
            )

        else:

            self.timer.start()
            self.cat_movie.start()

            self.start_button.setText(
                "Ⅱ"
            )

        self.setFocus()

    # ======================================================
    # MANUEL MOLA
    # ======================================================

    def toggle_break(self):

        self.timer.stop()
        self.cat_movie.stop()

        if self.current_session == "work":

            self.current_session = (
                "short_break"
            )

        else:

            self.current_session = (
                "work"
            )

        self.reset_current_session()

        self.start_button.setText(
            "▶"
        )

        self.update()

        self.setFocus()

    # ======================================================
    # BİLDİRİM
    # ======================================================

    def show_notification(
        self,
        title,
        message
    ):

        if (
            self.tray_icon
            and QSystemTrayIcon.supportsMessages()
        ):

            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                4000
            )

    # ======================================================
    # ÇİZİM
    # ======================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        # ==================================================
        # ARKA PLAN
        # ==================================================

        gradient = QLinearGradient(
            0,
            0,
            0,
            self.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#0B0924")
        )

        gradient.setColorAt(
            0.55,
            QColor("#17113B")
        )

        gradient.setColorAt(
            1.0,
            QColor("#32175C")
        )

        painter.setBrush(
            gradient
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.drawRoundedRect(
            self.rect(),
            18,
            18
        )

        # ==================================================
        # YILDIZLAR
        # ==================================================

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

            painter.setBrush(
                QColor("#A875FF")
            )

            painter.drawRect(
                x,
                y,
                size,
                size
            )

        # ==================================================
        # PARILTILAR
        # ==================================================

        sparkles = [
            (25, 110),
            (105, 95),
            (215, 105),
            (290, 120),
        ]

        for x, y in sparkles:

            painter.setBrush(
                QColor("#C89BFF")
            )

            painter.drawRect(
                x,
                y,
                2,
                2
            )

            painter.drawRect(
                x - 2,
                y + 1,
                6,
                1
            )

            painter.drawRect(
                x + 1,
                y - 2,
                1,
                6
            )

        # ==================================================
        # KEDİ
        # ==================================================

        if self.cat_movie.isValid():

            cat_width = 120
            cat_height = 120

            cat_x = (
                self.width()
                - cat_width
            ) // 2

            cat_y = 18

            current_frame = (
                self.cat_movie.currentPixmap()
            )

            painter.drawPixmap(
                cat_x,
                cat_y,
                cat_width,
                cat_height,
                current_frame
            )

        # ==================================================
        # TIMER
        # ==================================================

        painter.setFont(
            self.timer_font
        )

        painter.setPen(
            QColor("#F0E7FF")
        )

        if self.timer_mode == "countdown":

            display_seconds = (
                self.remaining_seconds
            )

        else:

            display_seconds = (
                self.elapsed_seconds
            )

        minutes = (
            display_seconds // 60
        )

        seconds = (
            display_seconds % 60
        )

        time_text = (
            f"{minutes:02d}:{seconds:02d}"
        )

        painter.drawText(
            0,
            140,
            self.width(),
            38,
            Qt.AlignmentFlag.AlignCenter,
            time_text
        )

        # ==================================================
        # FOCUS / BREAK YAZISI
        # ==================================================

        painter.setFont(
            self.small_font
        )

        if self.current_session == "work":

            session_text = "FOCUS"

            session_color = QColor(
                "#D2B4FF"
            )

        elif self.current_session == "short_break":

            session_text = "SHORT BREAK"

            session_color = QColor(
                "#E8D4FF"
            )

        else:

            session_text = "LONG BREAK"

            session_color = QColor(
                "#FFD98A"
            )

        painter.setPen(
            session_color
        )

        painter.drawText(
            0,
            182,
            self.width(),
            18,
            Qt.AlignmentFlag.AlignCenter,
            session_text
        )

        # ==================================================
        # POMODORO SAYACI
        # ==================================================

        painter.setFont(
            QFont(
                self.small_font.family(),
                7
            )
        )

        painter.setPen(
            QColor("#9D86C5")
        )

        counter_text = (
            f"{self.completed_sessions} / "
            f"{self.sessions_before_long_break}"
        )

        painter.drawText(
            15,
            238,
            80,
            10,
            Qt.AlignmentFlag.AlignLeft,
            counter_text
        )

    # ======================================================
    # KLAVYE
    # ======================================================

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Space:

            self.toggle_timer()
            return

        if event.key() == Qt.Key.Key_R:

            self.reset_timer()
            return

        super().keyPressEvent(event)

    # ======================================================
    # SÜRÜKLEME
    # ======================================================

    def mousePressEvent(self, event):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):

        if (
            event.buttons()
            == Qt.MouseButton.LeftButton
            and self.drag_position
            is not None
        ):

            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

    def mouseReleaseEvent(self, event):

        self.drag_position = None


# ======================================================
# UYGULAMAYI BAŞLAT
# ======================================================

app = QApplication(sys.argv)

app.setQuitOnLastWindowClosed(True)

window = WizardCat()

window.show()

window.setFocus()

sys.exit(
    app.exec()
)
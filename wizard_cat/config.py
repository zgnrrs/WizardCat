import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_before_long_break": 4,
    "timer_mode": "countdown",
    "auto_start_breaks": True,
    "auto_start_focus": False,
    "theme": "wizard_purple",
}


def load_settings() -> dict:
    """Load application settings from JSON file or return defaults."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)
        return settings
    except Exception as error:
        print("Ayarlar yüklenemedi:", error)
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    """Save application settings to JSON file."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)
    except Exception as error:
        print("Ayarlar kaydedilemedi:", error)

import json
import os
from typing import Tuple

RPG_FILE = "rpg_stats.json"

TITLES = [
    (1, "Novice Apprentice 🪄"),
    (3, "Spellcaster 🔮"),
    (5, "Star Weaver ✨"),
    (8, "Potion Master 🧪"),
    (10, "Archmage Cat 👑"),
]


class RPGStats:
    """Manages Wizard Cat leveling, EXP calculations, titles, and stats persistence."""

    def __init__(
        self,
        level: int = 1,
        exp: int = 0,
        total_exp: int = 0,
        spells_cast: int = 0,
        total_focus_minutes: int = 0,
    ):
        self.level = max(1, level)
        self.exp = max(0, exp)
        self.total_exp = max(0, total_exp)
        self.spells_cast = max(0, spells_cast)
        self.total_focus_minutes = max(0, total_focus_minutes)

    @property
    def required_exp(self) -> int:
        """EXP required to reach the next level."""
        return self.level * 100

    @property
    def title(self) -> str:
        """Current Wizard Cat title based on level."""
        current_title = TITLES[0][1]
        for min_lvl, title_name in TITLES:
            if self.level >= min_lvl:
                current_title = title_name
            else:
                break
        return current_title

    def add_exp(self, amount: int, focus_minutes: int = 0) -> Tuple[bool, int, str]:
        """Award EXP to the wizard. Returns (leveled_up, new_level, new_title)."""
        if amount <= 0:
            return False, self.level, self.title

        self.exp += amount
        self.total_exp += amount
        self.spells_cast += 1
        self.total_focus_minutes += focus_minutes

        leveled_up = False
        while self.exp >= self.required_exp:
            self.exp -= self.required_exp
            self.level += 1
            leveled_up = True

        return leveled_up, self.level, self.title

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "exp": self.exp,
            "total_exp": self.total_exp,
            "spells_cast": self.spells_cast,
            "total_focus_minutes": self.total_focus_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RPGStats":
        return cls(
            level=data.get("level", 1),
            exp=data.get("exp", 0),
            total_exp=data.get("total_exp", 0),
            spells_cast=data.get("spells_cast", 0),
            total_focus_minutes=data.get("total_focus_minutes", 0),
        )


def load_rpg_stats() -> RPGStats:
    """Load RPG statistics from JSON file or return new RPGStats instance."""
    if not os.path.exists(RPG_FILE):
        return RPGStats()

    try:
        with open(RPG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return RPGStats.from_dict(data)
    except Exception as error:
        print("RPG stats yüklenemedi:", error)
        return RPGStats()


def save_rpg_stats(stats: RPGStats) -> None:
    """Save RPG statistics to JSON file."""
    try:
        with open(RPG_FILE, "w", encoding="utf-8") as f:
            json.dump(stats.to_dict(), f, indent=4, ensure_ascii=False)
    except Exception as error:
        print("RPG stats kaydedilemedi:", error)

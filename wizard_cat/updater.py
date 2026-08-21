import json
import re
import urllib.request
from PySide6.QtCore import QThread, Signal

from wizard_cat import __version__

GITHUB_REPO = "YagmurrCengiz/WizardCat"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def parse_version(ver_str: str) -> tuple:
    """Parse version string like 'v1.2.0' or '1.0' into tuple of integers."""
    clean_ver = re.sub(r"[^\d.]", "", ver_str)
    try:
        return tuple(map(int, clean_ver.split(".")))
    except ValueError:
        return (0, 0, 0)


def is_newer_version(remote_ver: str, current_ver: str) -> bool:
    """Compare remote version string against current version."""
    return parse_version(remote_ver) > parse_version(current_ver)


class CheckUpdateThread(QThread):
    """Background thread to query GitHub Releases API for new updates without blocking GUI."""

    update_available = Signal(str, str)  # (tag_name, download_url)

    def run(self):
        try:
            req = urllib.request.Request(
                RELEASES_API_URL,
                headers={"User-Agent": "WizardCat-App/1.0"},
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    tag_name = data.get("tag_name", "")
                    html_url = data.get(
                        "html_url",
                        f"https://github.com/{GITHUB_REPO}/releases",
                    )

                    if tag_name and is_newer_version(tag_name, __version__):
                        self.update_available.emit(tag_name, html_url)
        except Exception as err:
            print("GitHub update check skipped:", err)

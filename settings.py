import json
import os
from utils import get_appdata_folder, resource_path

class SettingsManager:
    def __init__(self):
        self.settings_path = os.path.join(get_appdata_folder(), "usage.json")
        self.character_limit = 5000
        self.character_limit_per_month = 1000000
        self.safety_margin = 10000
        self.characters_used = 0
        self.selected_language = "English-UK"
        self.selected_voice = "Leda"
        self.selected_device = None
        self.monitor_device = None
        self.monitor_enabled = True
        self.google_api_json = resource_path("client_auth_moontts.json")
        self.volume = 1.0
        self._load()

    def _load(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r") as f:
                    data = json.load(f)
                    self.characters_used = data.get("characters_used", 0)
                    self.selected_language = data.get("selected_language", "English-UK")
                    self.selected_voice = data.get("selected_voice", "Leda")
                    self.selected_device = data.get("last_selected_device", None)
                    self.monitor_device = data.get("last_monitor_device", None)
                    self.monitor_enabled = data.get("monitor_enabled", True)
                    self.google_api_json = data.get("google_api_json", self.google_api_json)
                    self.volume = data.get("volume", 1.0)
            except Exception:
                pass

    def save(self):
        data = {
            "characters_used": self.characters_used,
            "selected_language": self.selected_language,
            "selected_voice": self.selected_voice,
            "last_selected_device": self.selected_device,
            "last_monitor_device": self.monitor_device,
            "monitor_enabled": self.monitor_enabled,
            "google_api_json": self.google_api_json,
            "volume": self.volume,
        }
        with open(self.settings_path, "w") as f:
            json.dump(data, f)

    def load_voice_data(self):
        voices_path = resource_path("voices.json")
        with open(voices_path, "r", encoding="utf-8") as f:
            return json.load(f)
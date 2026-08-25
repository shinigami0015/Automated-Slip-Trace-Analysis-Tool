# -*- coding: utf-8 -*-
"""
ASTA Tool -- Session Memory
Saves and loads user preferences and folder paths.
"""
import os
import json

SETTINGS_FILE = "ASTA Tool_settings.json"

DEFAULT_SETTINGS = {
    "is_dark_mode": True,
    "scripts_folder": "",
    "input_folder": "",
    "output_folder": "",
    "loading_direction": "X",
    "ca_ratio": 1.5930,
    "crystal_system": "HCP + BCC"
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge with defaults to ensure all keys exist
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception:
        pass

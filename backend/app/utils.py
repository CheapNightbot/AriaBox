import json
import os

from flask import current_app


def get_current_settings() -> dict:
    """Helper function that reads and returns the actual runtime settings from settings.json."""
    settings_file = current_app.config.get("SETTINGS_FILE")

    # If the file exists, read it directly!
    if settings_file and os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)

    # If it doesn't exist yet, just return the defaults from config.py
    return {
        "language": current_app.config.get("DEFAULT_LANGUAGE", "en"),
        "location": current_app.config.get("DEFAULT_LOCATION", "US"),
        "enable_downloads": False,
    }


ALLOWED_EXTENSIONS = {
    "mp3",
    "wav",
    "flac",
    "m4a",
    "ogg",
    "opus",
    "aac",
    "wma",
    "alac",
}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

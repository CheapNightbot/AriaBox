import json
import os

from flask import Blueprint, current_app, request

bp = Blueprint("settings", __name__, url_prefix="/api")


def get_default_settings():
    """Helper function to get defaults from config.py"""
    return {
        "language": current_app.config.get("DEFAULT_LANGUAGE", "en"),
        "location": current_app.config.get("DEFAULT_LOCATION", "US"),
    }


@bp.route("settings", methods=["GET"])
def get_settings():
    settings_file = current_app.config.get("SETTINGS_FILE")
    assert settings_file

    # Check if the settings file already exists
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            settings = json.load(f)
    # First time running! Create it with default values from config.py
    else:
        settings = get_default_settings()
        # Ensure the config directory exists (just in case)
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)

    return settings, 200


@bp.route("settings", methods=["POST", "PUT"])
def update_settings():
    data = request.get_json()
    if not data:
        return {"message": "No data provided!"}, 400

    settings_file = current_app.config.get("SETTINGS_FILE")
    assert settings_file

    # Load existing settings, or fall back to defaults
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            settings = json.load(f)
    else:
        settings = get_default_settings()

    # Update only the fields that were sent
    if "language" in data:
        settings["language"] = data["language"]
    if "location" in data:
        settings["location"] = data["location"]

    # Save the updated settings back to the file
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)

    return settings, 200

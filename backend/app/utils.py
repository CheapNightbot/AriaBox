import json
import logging
import os
import threading
import time
from pathlib import Path

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
        "auto_save_to_library": False,
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


def start_temp_cleanup_thread(temp_dir: Path):
    """
    Starts a background daemon thread that cleans up files in the `DATA_DIR/temp` directory
    older than 24 hours.
    """

    logger = logging.getLogger("ariabox.cleanup")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Don't rely on root logger's handler

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        logging.Formatter(
            "[%(levelname)-8s] %(asctime)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %I:%M:%S %p",
        )
    )
    logger.addHandler(handler)

    def cleanup_loop():
        # Wait 5 minutes on startup so we don't interfere with active uploads
        time.sleep(300)

        while True:
            try:
                try:
                    file_paths = list(temp_dir.iterdir())
                except FileNotFoundError:
                    # `DATA_DIR/temp` directory doesn't exist yet or was removed
                    logger.debug("Temp directory not found; skipping cleanup cycle.")
                else:
                    now = time.time()
                    deleted_count = 0

                    for file_path in file_paths:
                        if file_path.is_file():
                            # Check if file is older than 24 hours (86400 seconds)
                            if now - file_path.stat().st_mtime > 86400:
                                try:
                                    file_path.unlink()
                                    deleted_count += 1
                                except OSError as e:
                                    logger.warning(f"Could not delete {file_path}: {e}")

                    if deleted_count > 0:
                        logger.info(
                            f"🧹 Background cleanup: Removed {deleted_count} old temp file(s)."
                        )

            except Exception as e:
                logger.warning(f"Background temp cleanup failed: {e}", exc_info=True)

            # Sleep for 1 hour before checking again
            time.sleep(3600)

    # Create a daemon thread (it will automatically die when the main app stops)
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()

import json
import logging
import os
import re
import threading
import time
from pathlib import Path

from app.tagger import Metadata
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
        "download_format": "mp3",
        "prompt_for_format": True,
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


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename for modern filesystems.
    Keeps UTF-8 characters (like Japanese) and spaces, but removes
    illegal characters like / \\ : * ? " < > |
    """
    # Remove invalid filesystem characters
    sanitized = re.sub(r'[\\/:*?"<>|]', "", filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # Limit length to 200 characters (filesystem limit is usually 255)
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:200] + ext

    return sanitized if sanitized else "Unknown"


def generate_filename(metadata: Metadata, file_ext: str) -> str:
    """Safely generate a filename from metadata, including track number if available."""
    artist = "Unknown Artist"
    if metadata.artists and len(metadata.artists) > 0:
        for name in metadata.artists:
            if name and name.strip():
                artist = name.strip()
                break

    title = metadata.title or "Unknown Title"

    # Add track number prefix if available (e.g., "01 - Title")
    if metadata.track_number:
        track_str = str(metadata.track_number).zfill(2)  # Pad with zero: 1 -> "01"
        if metadata.total_tracks:
            track_str = track_str.zfill(2)  # Ensure 2 digits
        return f"{track_str} - {artist} - {title}.{file_ext}"

    return f"{artist} - {title}.{file_ext}"


def get_organized_library_path(
    data_dir: str, metadata: Metadata, file_ext: str
) -> Path:
    """
    Generate an organized library path.
    - Albums: music/Artist/Album (Year)/01 - Track.ext
    - Singles: music/Artist/01 - Track.ext
    """
    music_dir = Path(data_dir) / "music"
    artist_name = sanitize_filename(
        metadata.artists[0] if metadata.artists else "Unknown Artist"
    )

    is_album = bool(
        metadata.album
        and metadata.album.strip()
        and metadata.album.lower() != "unknown album"
    )

    # ALWAYS include track number if available, for better library organization!
    if metadata.track_number:
        track_str = str(metadata.track_number).zfill(2)
        filename = f"{track_str} - {sanitize_filename(metadata.title or 'Unknown Title')}.{file_ext}"
    else:
        filename = f"{sanitize_filename(metadata.title or 'Unknown Title')}.{file_ext}"

    if is_album:
        # Extract year from release_date (e.g., "2023-10-27" -> "2023")
        year = ""
        if metadata.release_date:
            year_match = re.search(r"\b\d{4}\b", str(metadata.release_date))
            if year_match:
                year = f" ({year_match.group()})"

        album_name = sanitize_filename(f"{metadata.album or 'Unknown Album'}{year}")
        final_path = music_dir / artist_name / album_name / filename
    else:
        final_path = music_dir / artist_name / filename

    # Handle duplicate filenames gracefully
    counter = 1
    original_filename = filename

    while final_path.exists():
        name_without_ext, ext = os.path.splitext(original_filename)
        new_filename = f"{name_without_ext} ({counter}){ext}"
        if is_album:
            year = ""
            if metadata.release_date:
                year_match = re.search(r"\b\d{4}\b", str(metadata.release_date))
                if year_match:
                    year = f" ({year_match.group()})"
            album_name = sanitize_filename(f"{metadata.album or 'Unknown Album'}{year}")
            final_path = music_dir / artist_name / album_name / new_filename
        else:
            final_path = music_dir / artist_name / new_filename
        counter += 1

    return final_path


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

import hashlib
import os
import re

from flask import Blueprint, current_app, request

from app.logger import logger
from app.utils import ALLOWED_EXTENSIONS, allowed_file

bp = Blueprint("upload", __name__, url_prefix="/api")


@bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return {"message": "No file part in the request!"}, 400

    file = request.files["file"]
    if not file.filename:
        return {"message": "No file selected!"}, 400

    # Check if it's a valid audio file.
    if not allowed_file(file.filename):
        return {
            "message": (
                "File type not allowed. Please upload one of: "
                f"{', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        }, 400

    max_file_size = current_app.config["MAX_AUDIO_FILE_BYTES"]

    # Calculate SHA-256 and enforce the per-file size limit.
    file_hash = hashlib.sha256()
    file_size = 0

    for chunk in iter(lambda: file.stream.read(8192), b""):
        file_size += len(chunk)
        if file_size > max_file_size:
            return {
                "message": "This file is too large. Please choose an audio file no larger than 100 MiB (about 105 MB)."
            }, 413
        file_hash.update(chunk)

    file_id = file_hash.hexdigest()

    # Reset file stream to the beginning so it can be saved.
    file.stream.seek(0)

    # Get the original filename and extension.
    original_filename = os.path.basename(file.filename)
    ext = os.path.splitext(original_filename)[1].lower()

    safe_filename = f"{file_id}{ext}"

    # Save the file to the temp folder.
    data_dir = current_app.config.get("DATA_DIR")
    if not data_dir:
        return {"message": "Server configuration error."}, 500

    temp_dir = os.path.join(data_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(temp_dir, safe_filename)

    # Deduplication check.
    if os.path.exists(file_path):
        logger.info("Duplicate file detected! Returning existing file_id: %s", file_id)
    else:
        file.save(file_path)
        logger.info("File uploaded and saved to %s", file_path)

    # Try to extract the artist and song from the filename.
    name_without_ext = os.path.splitext(original_filename)[0]

    # Remove track numbers like "01. ", "1 - ", or "01 ".
    name_without_ext = re.sub(r"^\d+[\.\-\s]+", "", name_without_ext).strip()

    # Remove common suffixes like "(Official Video)", "[HQ]", "(Remastered)".
    name_without_ext = re.sub(r"[\(\[].*?[\)\]]", "", name_without_ext).strip()

    suggested_artist = ""
    suggested_song = name_without_ext

    # Split by " - " if it exists (e.g., "Artist - Song.mp3").
    if " - " in name_without_ext:
        parts = name_without_ext.split(" - ", 1)
        suggested_artist = parts[0].strip()
        suggested_song = parts[1].strip()

    return {
        "file_id": file_id,
        "original_filename": original_filename,
        "suggested_artist": suggested_artist,
        "suggested_song": suggested_song,
    }

import hashlib
import os
import re

from app.logger import logger
from app.utils import ALLOWED_EXTENSIONS, allowed_file
from flask import Blueprint, current_app, request

bp = Blueprint("upload", __name__, url_prefix="/api")


@bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return {"message": "No file part in the request!"}, 400

    file = request.files["file"]
    if not file.filename:
        return {"message": "No file selected!"}, 400

    # Check if it's a valid audio file
    if not allowed_file(file.filename):
        return {
            "message": f"File type not allowed. Please upload one of: {', '.join(ALLOWED_EXTENSIONS)}"
        }, 400

    # Calculate SHA-256 hash of the file (memory efficient, chunk by chunk)
    file_hash = hashlib.sha256()
    for chunk in iter(lambda: file.stream.read(8192), b""):
        file_hash.update(chunk)

    file_id = file_hash.hexdigest()

    # Reset file stream to the beginning so we can save it!
    file.stream.seek(0)

    # Get original filename & extension
    original_filename = os.path.basename(file.filename)
    ext = os.path.splitext(original_filename)[1].lower()

    safe_filename = f"{file_id}{ext}"

    # Save it to the temp folder!
    data_dir = current_app.config.get("DATA_DIR")
    assert data_dir
    temp_dir = os.path.join(data_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(temp_dir, safe_filename)

    # Deduplication check ~
    if os.path.exists(file_path):
        logger.info(f"Duplicate file detected! Returning existing file_id: {file_id}")
    else:
        # Save the file to disk only if it's new
        file.save(file_path)
        logger.info(f"File uploaded and saved to {file_path}")

    # Try to extract the artist & song from the filename!
    name_without_ext = os.path.splitext(original_filename)[0]

    # Clean up the filename using regex ~
    # Remove track numbers like "01. ", "1 - ", "01 "
    name_without_ext = re.sub(r"^\d+[\.\-\s]+", "", name_without_ext).strip()
    # Remove common suffixes like "(Official Video)", "[HQ]", "(Remastered)"
    name_without_ext = re.sub(r"[\(\[].*?[\)\]]", "", name_without_ext).strip()

    suggested_artist = ""
    suggested_song = name_without_ext

    # Split by " - " if it exists (e.g., "Artist - Song.mp3")
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

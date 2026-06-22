import os
import re
import uuid

from flask import Blueprint, current_app, request

from app.logger import logger
from app.utils import allowed_file, ALLOWED_EXTENSIONS

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

    # Generate a unique ID so we don't overwrite files!
    file_id = uuid.uuid4().hex
    original_filename = os.path.basename(file.filename)

    # Figure out the file extension
    ext = os.path.splitext(original_filename)[1].lower()
    safe_filename = f"{file_id}{ext}"

    # Save it to the temp folder!
    data_dir = current_app.config.get("DATA_DIR")
    assert data_dir
    temp_dir = os.path.join(data_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(temp_dir, safe_filename)
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

import re
from pathlib import Path

from flask import Blueprint, current_app, request

from app.logger import logger
from app.utils import ALLOWED_EXTENSIONS

bp = Blueprint("delete", __name__, url_prefix="/api")


@bp.route("/delete", methods=["DELETE"])
def delete_file():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"message": "No valid JSON object provided!"}, 400

    file_id = data.get("file_id")
    file_ext = data.get("file_ext")

    if not isinstance(file_id, str) or not re.fullmatch(r"[0-9a-f]{64}", file_id):
        return {"message": "Invalid file ID."}, 400

    if not isinstance(file_ext, str):
        return {"message": "Invalid file extension."}, 400

    # Accept "mp3" or ".mp3", but reject multiple leading dots.
    if file_ext.startswith("."):
        file_ext = file_ext[1:]
    file_ext = file_ext.lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        return {"message": "Invalid file extension."}, 400

    data_dir = current_app.config.get("DATA_DIR")
    if not data_dir:
        logger.error("DATA_DIR configuration missing.")
        return {"message": "Server configuration error."}, 500

    base_path = Path(data_dir).resolve()
    temp_dir = (base_path / "temp").resolve()

    try:
        # Ensure the temp directory itself resolves under DATA_DIR.
        temp_dir.relative_to(base_path)

        # strict=True requires that the candidate already exists.
        file_path = (temp_dir / f"{file_id}.{file_ext}").resolve(strict=True)

        # Check directory containment using path components.
        file_path.relative_to(temp_dir)
    except (OSError, ValueError):
        return {"message": "The requested file does not exist or is invalid."}, 404

    if not file_path.is_file():
        return {"message": "The requested file does not exist or is not a file."}, 404

    try:
        file_path.unlink()
        return "", 204
    except FileNotFoundError:
        return {"message": "The requested file does not exist."}, 404
    except PermissionError:
        logger.error("Permission denied deleting file: %s", file_path)
        return {"message": "Permission denied."}, 403
    except OSError:
        logger.exception("Failed to delete file: %s", file_path)
        return {"message": "Internal server error."}, 500

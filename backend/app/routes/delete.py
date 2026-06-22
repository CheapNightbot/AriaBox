from pathlib import Path

from flask import Blueprint, abort, current_app, request
from werkzeug.utils import secure_filename

from app.logger import logger
from app.utils import ALLOWED_EXTENSIONS

bp = Blueprint("delete", __name__, url_prefix="/api")


@bp.route("/delete", methods=["DELETE"])
def delete_file():
    data = request.get_json()
    if not data:
        return {"message": "No data provided!"}, 400

    file_id = data.get("file_id")
    file_ext = data.get("file_ext")
    if not file_id or not file_ext:
        return {"message": "Invalid file ID provided!"}, 400

    file_id = secure_filename(file_id)
    file_ext = secure_filename(file_ext)

    if file_ext not in ALLOWED_EXTENSIONS:
        return {"message": "Invalid file extension."}, 400

    data_dir = current_app.config.get("DATA_DIR")
    if not data_dir:
        logger.error("DATA_DIR configuration missing.")
        abort(500, description="Server configuration error.")

    base_path = Path(data_dir).resolve()
    file_path = (base_path / "temp" / f"{file_id}.{file_ext}").resolve()

    if file_path.is_file():
        try:
            file_path.unlink()
            return "", 204
        except PermissionError:
            logger.error(f"Permission denied deleting file: {file_path}")
            return {"message": "Permission denied."}, 403
        except Exception as e:
            logger.exception(f"Failed to delete file: {e}")
            return {"message": "Internal server error."}, 500
    else:
        return {"message": "The requested file does not exist or is not a file."}, 404

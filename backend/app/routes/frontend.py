import os

from flask import Blueprint, current_app, send_from_directory

bp = Blueprint("frontend", __name__)


@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
def serve_frontend(path):
    dist_dir = current_app.config.get("FRONTEND_DIST_DIR")
    assert dist_dir

    # If the specific file exists (like a CSS or JS file), send it!
    if path and os.path.exists(os.path.join(dist_dir, path)):
        return send_from_directory(dist_dir, path)

    # Otherwise, send the main index.html so React Router can take over!
    return send_from_directory(dist_dir, "index.html")

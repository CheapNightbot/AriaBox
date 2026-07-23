import os
import secrets
from pathlib import Path

from app.utils import start_temp_cleanup_thread
from config import Config
from flask import Flask


def create_app(config=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)

    # Make sure the data directories exists!
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.CONFIG_DIR, exist_ok=True)

    # Start the background cleanup thread
    start_temp_cleanup_thread(Path(config.DATA_DIR, "temp"))

    # Make sure secret key was passed, otherwise generate new one
    # No environment variable was provided.
    if not app.config.get("SECRET_KEY"):
        # Check if previously generated one exists.
        if os.path.exists(config.SECRET_KEY_FILE):
            with open(config.SECRET_KEY_FILE, "r") as f:
                app.config["SECRET_KEY"] = f.read().strip()
            print(
                "⚠️ [WARNING] No SECRET_KEY in environment. Using auto-generated key from .secret_key file."
            )
        # No previously generated secret. Generate new one, use and save it.
        else:
            new_secret = secrets.token_hex()
            with open(config.SECRET_KEY_FILE, "w") as f:
                f.write(new_secret)
            app.config["SECRET_KEY"] = new_secret
            print(
                "⚠️ [WARNING] No SECRET_KEY provided! Auto-generated and saved to .secret_key. Please set SECRET_KEY in .env for production!"
            )
    # Environment variable WAS provided!
    else:
        # Clean up any old auto-generated file.
        if os.path.exists(config.SECRET_KEY_FILE):
            os.remove(config.SECRET_KEY_FILE)
            print(
                "✅ [INFO] Using SECRET_KEY from environment. Removed old .secret_key file."
            )

    # Register blueprints
    from .routes import (
        cache,
        convert,
        delete,
        download,
        frontend,
        search,
        settings,
        tag,
        upload,
    )

    if app.debug:
        app.register_blueprint(cache.bp)
    app.register_blueprint(convert.bp)
    app.register_blueprint(delete.bp)
    app.register_blueprint(download.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(tag.bp)
    app.register_blueprint(upload.bp)
    # Register frontend LAST so it doesn't accidentally catch /api requests!
    app.register_blueprint(frontend.bp)

    return app

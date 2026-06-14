import os

from dotenv import load_dotenv

load_dotenv()

backend_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.dirname(backend_dir)


class Config:
    DATA_DIR = os.getenv("DATA_DIR", f"{project_root}/data")
    CONFIG_DIR = os.path.join(DATA_DIR, ".config")
    SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
    SECRET_KEY_FILE = os.path.join(CONFIG_DIR, ".secret_key")

    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
    DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "US")

    FRONTEND_DIST_DIR = os.getenv(
        "FRONTEND_DIST_DIR", os.path.join(project_root, "frontend", "dist")
    )

    HOST_URL = os.getenv("HOST_URL", "0.0.0.0")
    HOST_PORT = int(os.getenv("HOST_PORT", 8960))

    SECRET_KEY = os.getenv("SECRET_KEY")

import logging
import os
import sys

logger = logging.getLogger("ariabox")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)

if os.environ.get("FLASK_DEBUG", "0") in ("1", "true", "True"):
    handler.setLevel(logging.INFO)
else:
    handler.setLevel(logging.WARNING)

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
)
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)

import logging
import sys

logger = logging.getLogger("ariabox")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
)
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)

from flask import Blueprint

from app.cache import get_cache_stats, clear_cache as cc

bp = Blueprint("cache", __name__, url_prefix="/api")


@bp.route("/cache/stats", methods=["GET"])
def cache_stats():
    """Get cache statistics."""
    return get_cache_stats()


@bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Clear all cache entries."""
    msg = cc()
    return {"message": msg}

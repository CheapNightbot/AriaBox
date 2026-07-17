from flask import Blueprint

from app.cache import clear_expired_cache, get_cache_stats

bp = Blueprint("cache", __name__, url_prefix="/api")


@bp.route("/cache/stats", methods=["GET"])
def cache_stats():
    """Get cache statistics."""
    return get_cache_stats()


@bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Clear all expired cache entries."""
    msg = clear_expired_cache()
    return {"message": msg}

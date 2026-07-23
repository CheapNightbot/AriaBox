"""
Simple in-memory cache for search results.
Caches search results and individual items.

NOTE: While it okie for now, maybe me should consider using
something like redis or similar. Because (especially for me),
many free hosting provider provide very low RAM on free plan.
So (unlikely) we can hit memory limit causing crashes and stuff ~
"""

import hashlib
import time
from typing import Optional

from app.logger import logger

# Cache structure: { key: {"data": ..., "timestamp": ...} }
_search_cache: dict[str, dict] = {}

# Cache expires after 30 minutes for searches, 1 hour for individual items
SEARCH_CACHE_TTL = 1800  # 30 minutes
ITEM_CACHE_TTL = 3600  # 1 hour


def _hash_query(artist: str, song: str, location: str) -> str:
    """Create a unique hash for a search query."""
    query = f"{artist}:{song}:{location}"
    return hashlib.md5(query.encode()).hexdigest()


def get_cached_search(artist: str, song: str, location: str) -> Optional[dict]:
    """
    Check if we have cached results for this search query.
    Returns None if not found or expired.
    """
    query_hash = _hash_query(artist, song, location)
    key = f"search:{query_hash}"

    cached = _search_cache.get(key)
    if not cached:
        return None

    # Check if expired
    if time.time() - cached["timestamp"] > SEARCH_CACHE_TTL:
        del _search_cache[key]
        logger.debug(f"Search cache expired for '{artist} - {song}'")
        return None

    logger.info(f"Cache hit for search: '{artist} - {song}'")
    return cached["data"]


def store_search_cache(artist: str, song: str, location: str, results: dict):
    """Cache search results for a query."""
    query_hash = _hash_query(artist, song, location)
    key = f"search:{query_hash}"

    _search_cache[key] = {
        "data": results,
        "timestamp": time.time(),
    }

    logger.info(f"Cached search results for '{artist} - {song}'")


def cache_key(service: str, item_id: int) -> str:
    """Generate a unique cache key for an individual item."""
    return f"item:{service}:{item_id}"


def _store_search_result(service: str, item_id: int, data: dict):
    """Internal helper: Store an individual search result in the cache."""
    key = cache_key(service, item_id)
    _search_cache[key] = {
        "data": data,
        "timestamp": time.time(),
    }
    logger.debug(f"Cached {service} item: {item_id}")


def get_cached_result(service: str, item_id: int) -> Optional[dict]:
    """
    Retrieve a cached individual item.
    Returns None if not found or expired.
    """
    key = cache_key(service, item_id)
    cached = _search_cache.get(key)

    if not cached:
        return None

    # Check if expired (use longer TTL for items)
    if time.time() - cached["timestamp"] > ITEM_CACHE_TTL:
        del _search_cache[key]
        logger.debug(f"Item cache expired for {service}:{item_id}")
        return None

    logger.debug(f"Item cache hit for {service}:{item_id}")
    return cached["data"]


def store_search_results(service: str, items: list):
    """Store multiple search results at once."""
    for item in items:
        if hasattr(item, "id") and item.id:
            from dataclasses import asdict

            try:
                data = asdict(item)
                _store_search_result(service, item.id, data)
            except Exception as e:
                logger.warning(f"Failed to cache {service} item {item.id}: {e}")


def clear_expired_cache():
    """Remove all expired entries from the cache."""
    now = time.time()
    expired_keys = [
        key
        for key, value in _search_cache.items()
        if now - value["timestamp"] > ITEM_CACHE_TTL  # Use the longer TTL
    ]
    for key in expired_keys:
        del _search_cache[key]

    if expired_keys:
        msg = f"Successfully cleared {len(expired_keys)} expired entries!"
        logger.info(msg)
        return msg

    return "Cache is already clean! No expired entries found."


def get_cache_stats() -> dict:
    """Get cache statistics (useful for debugging)."""
    search_count = sum(1 for k in _search_cache if k.startswith("search:"))
    item_count = sum(1 for k in _search_cache if k.startswith("item:"))

    return {
        "total_entries": len(_search_cache),
        "search_queries": search_count,
        "individual_items": item_count,
        "memory_estimate_kb": len(str(_search_cache)) // 1024,
    }


def get_cached_tracks_for_album(service: str, album_id: str | int) -> list:
    """
    Scan the cache for all tracks that belong to the given album_id.
    """
    matching_tracks = []
    prefix = f"item:{service}:"
    target_album_id_str = str(album_id)

    for key, cached in _search_cache.items():
        if key.startswith(prefix):
            data = cached.get("data")
            if not data:
                continue

            # Check if this item is a track and belongs to the target album
            album_info = data.get("album")
            if (
                isinstance(album_info, dict)
                and str(album_info.get("id")) == target_album_id_str
            ):
                matching_tracks.append(data)

    # Sort by track_number if available to keep album order
    matching_tracks.sort(key=lambda x: x.get("track_number") or 696)

    if matching_tracks:
        logger.info(
            f"Found {len(matching_tracks)} cached tracks for {service} album {album_id}"
        )

    return matching_tracks

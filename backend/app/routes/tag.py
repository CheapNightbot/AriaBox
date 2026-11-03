import re
from pathlib import Path
from types import SimpleNamespace

from flask import Blueprint, current_app, request, send_file
from markupsafe import escape
from yutipy.deezer import Deezer
from yutipy.musicyt import MusicYT

from app.cache import get_cached_result
from app.logger import logger
from app.tagger import Metadata, tag_audio_file
from app.utils import (
    ALLOWED_EXTENSIONS,
    generate_filename,
    get_current_settings,
    get_organized_library_path,
    sanitize_filename,
)

bp = Blueprint("tag", __name__, url_prefix="/api")


@bp.route("/tag", methods=["POST"])
def tag_file():
    """
    Apply metadata to an uploaded audio file.

    Expected JSON:
    {
        "file_id": "abc123",
        "file_ext": "mp3",
        "track_id": 123,  # OR "album_id": 456
        "service": "deezer"  # or "itunes", "ytmusic", "YouTube Music"
    }
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"message": "No valid JSON object provided!"}, 400

    file_id = data.get("file_id")
    file_ext = data.get("file_ext")
    track_id = data.get("track_id")
    album_id = data.get("album_id")
    service = data.get("service")
    overwrite = data.get("overwrite", True)

    if not file_id or not file_ext or not service:
        return {"message": "Missing required fields!"}, 400

    if not isinstance(file_id, str) or not re.fullmatch(r"[0-9a-f]{64}", file_id):
        return {"message": "Invalid file ID."}, 400

    if not isinstance(file_ext, str):
        return {"message": "Invalid file extension."}, 400

    file_ext = file_ext.lower().lstrip(".")
    if file_ext not in ALLOWED_EXTENSIONS:
        return {"message": "Invalid file extension."}, 400

    if not isinstance(service, str):
        return {"message": "Unsupported music service."}, 400

    if not isinstance(overwrite, bool):
        return {"message": "The overwrite field must be a boolean."}, 400

    if not track_id and not album_id:
        return {"message": "Must provide either track_id or album_id!"}, 400

    # Normalize service names (handle "YouTube Music" -> "ytmusic", etc.)
    service_map = {
        "deezer": "deezer",
        "itunes": "itunes",
        "youtube music": "ytmusic",
        "ytmusic": "ytmusic",
    }

    normalized_service = service_map.get(service.lower())

    if not normalized_service:
        return {"message": f"Unsupported service: {escape(service)}"}, 400

    # Resolve and validate the uploaded file path.
    data_dir = current_app.config.get("DATA_DIR")
    if not data_dir:
        return {"message": "Server configuration error."}, 500

    base_path = Path(data_dir).resolve()
    temp_dir = (base_path / "temp").resolve()

    try:
        temp_dir.relative_to(base_path)
        file_path = (temp_dir / f"{file_id}.{file_ext}").resolve(strict=True)
        file_path.relative_to(temp_dir)
    except (OSError, ValueError):
        return {"message": "File not found or invalid path."}, 404

    if not file_path.is_file():
        return {"message": "File not found. Please upload again."}, 404

    # Try to get metadata.
    metadata = None

    # First, check the cache (works for all services including iTunes).
    cached_data = None
    if track_id:
        cached_data = get_cached_result(normalized_service, track_id)
    elif album_id:
        cached_data = get_cached_result(normalized_service, album_id)

    if cached_data:
        try:
            if track_id:
                track_obj = SimpleNamespace(**cached_data)
                if cached_data.get("album"):
                    track_obj.album = SimpleNamespace(**cached_data["album"])
                if cached_data.get("artists"):
                    track_obj.artists = [
                        SimpleNamespace(**artist) for artist in cached_data["artists"]
                    ]
                metadata = Metadata.from_track(track_obj)
            else:
                album_obj = SimpleNamespace(**cached_data)
                if cached_data.get("artists"):
                    album_obj.artists = [
                        SimpleNamespace(**artist) for artist in cached_data["artists"]
                    ]
                metadata = Metadata.from_album(album_obj)

            logger.info(
                "Using cached metadata for %s:%s",
                normalized_service,
                track_id or album_id,
            )
        except Exception as e:
            logger.warning("Failed to use cached data: %s", e)
            metadata = None

    # If not in cache, try to fetch from the service.
    if not metadata:
        try:
            if normalized_service == "deezer":
                with Deezer() as deezer:
                    if track_id:
                        track = deezer.get_track(track_id)
                        if not track:
                            return {"message": "Track not found on Deezer."}, 404
                        metadata = Metadata.from_track(track)
                    else:
                        album = deezer.get_album(album_id)
                        if not album:
                            return {"message": "Album not found on Deezer."}, 404
                        metadata = Metadata.from_album(album)

            elif normalized_service == "ytmusic":
                with MusicYT() as ytmusic:
                    if track_id:
                        track = ytmusic.get_track(track_id)
                        if not track:
                            return {"message": "Track not found on YouTube Music."}, 404
                        metadata = Metadata.from_track(track)
                    else:
                        album = ytmusic.get_album(album_id)
                        if not album:
                            return {"message": "Album not found on YouTube Music."}, 404
                        metadata = Metadata.from_album(album)

            elif normalized_service == "itunes":
                # iTunes doesn't have get_track/get_album endpoints
                # and it's not in cache, so we can't proceed.
                return {
                    "message": (
                        "iTunes data not available. Please search again "
                        "to refresh the cache."
                    )
                }, 400

            else:
                return {"message": f"Unsupported service: {normalized_service}"}, 400

        except Exception:
            logger.exception(
                "Failed to fetch metadata from %s",
                normalized_service,
            )
            return {"message": "Failed to fetch metadata from music service."}, 500

    if not metadata:
        return {"message": "Could not retrieve metadata. Please search again."}, 404

    # Tag the file.
    success = tag_audio_file(file_path, metadata, overwrite=overwrite)

    if not success:
        return {"message": "Failed to apply metadata."}, 500

    # Check if the user wants to auto-save to the library.
    settings = get_current_settings()
    auto_save = settings.get("auto_save_to_library", False)

    if auto_save:
        final_path = get_organized_library_path(str(base_path), metadata, file_ext)

        # Create nested directories if they don't exist.
        final_path.parent.mkdir(parents=True, exist_ok=True)

        # Move the file.
        file_path.rename(final_path)
        logger.info("File saved to organized library: %s", final_path)

        return {
            "message": "Metadata applied and saved to library!",
            "saved_to": str(final_path),
        }, 200

    # Send the file to the browser.
    raw_filename = generate_filename(metadata, file_ext)
    download_name = sanitize_filename(raw_filename)

    return send_file(
        file_path,
        as_attachment=True,
        download_name=download_name,
        mimetype=f"audio/{file_ext}" if file_ext != "mp3" else "audio/mpeg",
    )

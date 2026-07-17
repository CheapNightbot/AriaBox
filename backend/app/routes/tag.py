import os
import re
from pathlib import Path
from types import SimpleNamespace

from flask import Blueprint, current_app, request, send_file
from yutipy.deezer import Deezer
from yutipy.musicyt import MusicYT

from app.cache import get_cached_result
from app.logger import logger
from app.tagger import Metadata, tag_audio_file
from app.utils import get_current_settings

bp = Blueprint("tag", __name__, url_prefix="/api")


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename for modern filesystems.
    Keeps UTF-8 characters (like Japanese) and spaces, but removes
    illegal characters like / \\ : * ? " < > |
    """
    # Remove invalid filesystem characters
    sanitized = re.sub(r'[\\/:*?"<>|]', "", filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # Limit length to 200 characters (filesystem limit is usually 255)
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:200] + ext

    return sanitized if sanitized else "Unknown"


def generate_filename(metadata: Metadata, file_ext: str) -> str:
    """Safely generate a filename from metadata."""
    # Get artist name safely
    artist = "Unknown Artist"
    if metadata.artists and len(metadata.artists) > 0:
        # Take the first non-empty artist name
        for name in metadata.artists:
            if name and name.strip():
                artist = name.strip()
                break

    # Get title safely
    title = metadata.title or "Unknown Title"

    return f"{artist} - {title}.{file_ext}"


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
    data = request.get_json()
    if not data:
        return {"message": "No data provided!"}, 400

    file_id = data.get("file_id")
    file_ext = data.get("file_ext")
    track_id = data.get("track_id")
    album_id = data.get("album_id")
    service = data.get("service")
    overwrite = data.get("overwrite", True)

    if not file_id or not file_ext or not service:
        return {"message": "Missing required fields!"}, 400

    if not track_id and not album_id:
        return {"message": "Must provide either track_id or album_id!"}, 400

    # Normalize service names (handle "YouTube Music" -> "ytmusic", etc.)
    service_map = {
        "deezer": "deezer",
        "itunes": "itunes",
        "youtube music": "ytmusic",
        "ytmusic": "ytmusic",
    }

    normalized_service = service_map.get(service.lower() if service else "")

    if not normalized_service:
        return {"message": f"Unsupported service: {service}"}, 400

    # Build file path safely
    data_dir = current_app.config.get("DATA_DIR")
    if not data_dir:
        return {"message": "Server configuration error."}, 500

    base_path = Path(data_dir).resolve()
    file_path = (base_path / "temp" / f"{file_id}.{file_ext}").resolve()

    # Security check
    if not str(file_path).startswith(str(base_path / "temp")):
        return {"message": "Invalid file path!"}, 400

    if not file_path.is_file():
        return {"message": "File not found. Please upload again."}, 404

    # Try to get metadata
    metadata = None

    # First, check the cache (works for ALL services including iTunes!)
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
                        SimpleNamespace(**a) for a in cached_data["artists"]
                    ]
                metadata = Metadata.from_track(track_obj)
            else:
                album_obj = SimpleNamespace(**cached_data)
                if cached_data.get("artists"):
                    album_obj.artists = [
                        SimpleNamespace(**a) for a in cached_data["artists"]
                    ]
                metadata = Metadata.from_album(album_obj)

            logger.info(
                f"Using cached metadata for {normalized_service}:{track_id or album_id}"
            )
        except Exception as e:
            logger.warning(f"Failed to use cached data: {e}")
            metadata = None

    # If not in cache, try to fetch from service (works for Deezer/YouTube Music)
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
                # and it's not in cache, so we can't proceed
                return {
                    "message": "iTunes data not available. Please search again to refresh the cache."
                }, 400

            else:
                return {"message": f"Unsupported service: {normalized_service}"}, 400

        except Exception as e:
            logger.exception(f"Failed to fetch metadata from {normalized_service}: {e}")
            return {"message": "Failed to fetch metadata from music service."}, 500

    if not metadata:
        return {"message": "Could not retrieve metadata. Please search again."}, 404

    # Tag the file
    success = tag_audio_file(file_path, metadata, overwrite=overwrite)

    if not success:
        return {"message": "Failed to apply metadata."}, 500

    # Check if user wants to auto-save to library
    settings = get_current_settings()
    auto_save = settings.get("auto_save_to_library", False)

    if auto_save:
        # Move file to DATA_DIR/music/
        music_dir = base_path / "music"
        music_dir.mkdir(exist_ok=True)

        # Generate a safe filename using the helper function
        raw_filename = generate_filename(metadata, file_ext)
        safe_filename = sanitize_filename(raw_filename)
        final_path = music_dir / safe_filename

        # Handle duplicate filenames
        counter = 1
        while final_path.exists():
            raw_filename = generate_filename(metadata, file_ext)
            raw_filename = raw_filename.replace(
                f".{file_ext}", f" ({counter}).{file_ext}"
            )
            safe_filename = sanitize_filename(raw_filename)
            final_path = music_dir / safe_filename
            counter += 1

        # Move the file
        file_path.rename(final_path)

        logger.info(f"File saved to library: {final_path}")

        return {
            "message": "Metadata applied and saved to library!",
            "saved_to": str(final_path),
        }, 200

    else:
        # Send file to browser
        raw_filename = generate_filename(metadata, file_ext)
        download_name = sanitize_filename(raw_filename)

        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype=f"audio/{file_ext}" if file_ext != "mp3" else "audio/mpeg",
        )

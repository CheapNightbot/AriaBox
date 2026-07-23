import hashlib
import io
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from app.cache import get_cached_result, get_cached_tracks_for_album
from app.logger import logger
from app.tagger import Metadata, tag_audio_file
from app.utils import (
    generate_filename,
    get_current_settings,
    get_organized_library_path,
    sanitize_filename,
)
from flask import Blueprint, current_app, request, send_file
from markupsafe import escape
from yt_dlp import YoutubeDL
from yt_dlp.networking.impersonate import ImpersonateTarget
from yt_dlp.utils import DownloadError
from yutipy.deezer import Deezer
from yutipy.musicyt import MusicYT

bp = Blueprint("download", __name__, url_prefix="/api")


class YtDlpLogger:
    def __init__(self, app_logger):
        self.app_logger = app_logger

    def debug(self, msg: str):
        if msg.startswith("[debug]"):
            self.app_logger.debug(msg)

    def info(self, msg: str):
        self.app_logger.info(msg)

    def warning(self, msg: str):
        self.app_logger.warning(msg)

    def error(self, msg: str):
        self.app_logger.error(msg)


@bp.route("/download", methods=["POST"])
def download_audio():
    settings = get_current_settings()
    if not settings.get("enable_downloads"):
        return {"message": "Downloads are currently disabled."}, 403

    data = request.get_json()
    if not data:
        return {"message": "No data provided!"}, 400

    track_id = data.get("track_id")
    album_id = data.get("album_id")
    service = data.get("service")
    requested_format = data.get("format")

    if not service or (not track_id and not album_id):
        return {"message": "Missing required fields!"}, 400

    is_album = album_id is not None
    auto_save = settings.get("auto_save_to_library", False)

    service_map = {
        "deezer": "deezer",
        "itunes": "itunes",
        "youtube music": "ytmusic",
        "ytmusic": "ytmusic",
    }
    normalized_service = service_map.get(service.lower() if service else "")
    if not normalized_service:
        return {"message": f"Unsupported service: {escape(service)}"}, 400

    metadata = None
    tracks_to_download = []
    data_dir = current_app.config.get("DATA_DIR")

    if not data_dir:
        return {"message": "Server configuration error."}, 500

    # METADATA FETCHING STEP !!!!!!! It will be used to tag the downloaded audio ~
    # ----------------------
    if not is_album:
        # Use cache (results) for single track download.
        cached_data = get_cached_result(normalized_service, track_id)
        if cached_data:
            # Convert (cached) dict (and nested dicts) to SimpleNamespace object
            # as Metdata method expects an object from/of yutipy.models ~
            track_obj = SimpleNamespace(**cached_data)
            if cached_data.get("album"):
                track_obj.album = SimpleNamespace(**cached_data["album"])
            if cached_data.get("artists"):
                track_obj.artists = [
                    SimpleNamespace(**a) for a in cached_data["artists"]
                ]
            metadata = Metadata.from_track(track_obj)
            logger.info(
                f"Using cached metadata for track: {normalized_service}:{track_id}"
            )
        # Fallback to `get_track` method if cache is not found ~
        else:
            # Right now, iTunes class not have method to get a single track,
            # so if we not have the track in cache, we don't know anything about it!
            # TODO: will add (maybe) `get_track`/`get_album` methods in yutipy for iTunes,
            # till then www:
            if normalized_service == "itunes":
                return {
                    "message": "iTunes track data not available. Please search again to refresh the cache."
                }, 400

            try:
                if normalized_service == "deezer":
                    with Deezer() as deezer:
                        track = deezer.get_track(int(track_id))
                        if track:
                            metadata = Metadata.from_track(track)
                elif normalized_service == "ytmusic":
                    with MusicYT() as ytmusic:
                        track = ytmusic.get_track(str(track_id))
                        if track:
                            metadata = Metadata.from_track(track)
            except Exception as e:
                logger.exception(f"Failed to fetch live track: {e}")
                return {"message": "Failed to fetch metadata."}, 500

    else:
        # The album(s) returned from `search` method do not contain all the tracks data.
        # so for album, we must call `get_album` method, which has all the tracks and their info.
        # But again, iTunes class not have such method! Lukily for iTunes (Apple Music),
        # the search for an album also returns all the tracks that belong to that album.
        # That why, we scan our cache for all the tracks from iTunes that have this album id.
        if normalized_service == "itunes":
            # Scan cache for tracks belonging to this album_id
            cached_album_tracks = get_cached_tracks_for_album(
                normalized_service, str(album_id)
            )

            if cached_album_tracks:
                # Get first track & convert it's (nested) album to SimpleNamespace,
                # we'll use artist name & album title from it for zip filename,
                # because for some reason, me was always getting fallback value for artist name
                first_track = SimpleNamespace(**cached_album_tracks[0])
                if first_track.album and isinstance(first_track.album, dict):
                    album_obj = SimpleNamespace(**first_track.album)
                    metadata = Metadata.from_album(album_obj)
                else:
                    metadata = Metadata(title="Unknown Album", artists=[])

                # Convert all the cached (dict) tracks into SimpleNamespace list
                tracks_to_download = [SimpleNamespace(**t) for t in cached_album_tracks]
                logger.info(f"Using cached tracks for iTunes album: {album_id}")
            else:
                # TODO: me will (maybe w) add the `get_album` method to yutipy ~
                return {
                    "message": "iTunes album track data not found in cache. Please search for the album again OR download tracks individually from the Tracks tab."
                }, 400
        else:
            # Deezer / YTMusic: Call `get_album` to get full track list
            try:
                if normalized_service == "deezer":
                    with Deezer() as deezer:
                        album_obj = deezer.get_album(int(album_id))
                        if album_obj:
                            metadata = Metadata.from_album(album_obj)
                            tracks_to_download = album_obj.tracks or []
                elif normalized_service == "ytmusic":
                    with MusicYT() as ytmusic:
                        album_obj = ytmusic.get_album(str(album_id))
                        if album_obj:
                            metadata = Metadata.from_album(album_obj)
                            tracks_to_download = album_obj.tracks or []
            except Exception as e:
                logger.exception(f"Failed to fetch live album: {e}")
                return {"message": "Failed to fetch metadata."}, 500

    if not metadata:
        return {"message": "Could not retrieve metadata."}, 404

    temp_dir = Path(data_dir) / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    target_format = requested_format or settings.get("download_format", "mp3")
    user_location = settings.get("location", "US")

    ydl_opts: dict[str, Any] = {
        "format": "bestaudio/best",
        "paths": {"home": str(temp_dir)},
        "outtmpl": "%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": False,
        "noplaylist": True,
        "geo_bypass": True,
        "geo_bypass_country": user_location,
        "impersonate": ImpersonateTarget(
            client="safari", version="18.0", os="macos", os_version="15"
        ),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": target_format,
                "preferredquality": "320" if target_format == "mp3" else "0",
            }
        ],
        "js_runtimes": {"node": {}},
        "logger": YtDlpLogger(logger),
        "retries": 3,
        "extractor_retries": 3,
    }

    # DOWNLOADING & TAGGING STEP !!!!!!!! We use metadata fetched above for downloading & tagging ~
    # --------------------------
    processed_items = []

    if is_album:
        track_count = len(tracks_to_download or [])
        if track_count >= 20:
            import base64

            # 猫～(>/////< " )
            easter_egg_msg = base64.b64decode(
                "WW91IHRyaWVkIHRvIGRvd25sb2FkIHRoZSBlbnRpcmUgZGlzY29ncmFwaHkgYW5kIHlvdXIgc2VydmVyIGV4cGxvZGVkLiBNYXliZSBzdXBwb3J0IHRoZSBhcnRpc3RzIGluc3RlYWQ/"
            ).decode("utf-8")
            logger.warning(f"{easter_egg_msg}")
        else:
            logger.info(f"Downloading album with {track_count} tracks...")

        if not tracks_to_download:
            return {"message": "Could not retrieve track list for this album."}, 400

        for track in tracks_to_download or []:
            # Cast to Any to bypass strict Pylance dataclass checks
            track_any: Any = track

            # Convert nested album to SimpleNamespace object if it's a dict
            if isinstance(track_any.album, dict):
                track_any.album = SimpleNamespace(**track_any.album)
                if hasattr(track_any.album, "artists") and isinstance(
                    track_any.album.artists, list
                ):
                    new_artists = []
                    for a in track_any.album.artists:
                        if isinstance(a, dict):
                            new_artists.append(SimpleNamespace(**a))
                        else:
                            new_artists.append(a)  # Keep dataclass objects as-is!
                    track_any.album.artists = new_artists

            # Convert each artist in the track's artists list if it's a dict to SimpleNamespace object
            if isinstance(track_any.artists, list):
                new_artists = []
                for a in track_any.artists:
                    if isinstance(a, dict):
                        new_artists.append(SimpleNamespace(**a))
                    else:
                        new_artists.append(a)  # Keep dataclass objects as-is!
                track_any.artists = new_artists

            track_metadata = Metadata.from_track(track_any)

            # Check if already in library (auto-save)
            if auto_save:
                actual_ext = target_format if target_format != "m4a" else "m4a"
                final_path = get_organized_library_path(
                    str(data_dir), track_metadata, actual_ext
                )
                if final_path.exists():
                    logger.info(
                        f"Track already exists in library, skipping: {final_path.name}"
                    )
                    continue

            # ONLY use direct URL (of the track) if it's explicitly from YouTube Music!
            if normalized_service == "ytmusic" and getattr(track_any, "url", None):
                target_query = track_any.url
            else:
                # For Deezer, iTunes, or missing URLs, force YouTube search
                target_query = (
                    f"ytsearch1:{track_metadata.artists[0]} - {track_metadata.title}"
                )

            # Ensure target_query is a valid string
            if not target_query or not isinstance(target_query, str):
                logger.warning(
                    f"Could not determine download target for: {track_metadata.title}"
                )
                continue

            # Hash the query AND the target format!
            # Used as file name to prevent downloading same file agian ~
            query_hash = hashlib.md5(
                f"{target_query}:{target_format}".encode()
            ).hexdigest()
            existing_files = list(temp_dir.glob(f"{query_hash}.*"))

            if existing_files:
                logger.info(f"Reusing existing temp file for: {target_query}")
                dl_path = existing_files[0]
                tag_audio_file(dl_path, track_metadata, overwrite=True)
                processed_items.append((dl_path, track_metadata))
            else:
                logger.info(f"Downloading via yt-dlp: {target_query}")
                ydl_opts["outtmpl"] = f"{query_hash}.%(ext)s"
                try:
                    with YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                        ydl.download([target_query])

                    downloaded_files = list(temp_dir.glob(f"{query_hash}.*"))
                    if downloaded_files:
                        dl_path = downloaded_files[0]
                        tag_audio_file(dl_path, track_metadata, overwrite=True)
                        processed_items.append((dl_path, track_metadata))
                except Exception as e:
                    logger.warning(
                        f"Failed to download track '{track_metadata.title}': {e}"
                    )
                    continue

        # Prevent sending an empty zip file if ALL tracks failed!
        # For example, YT-sensei's 403 ~ ;w;
        if not processed_items:
            return {
                "message": "Failed to download tracks from this album. They might be unavailable or restricted."
            }, 500

    else:
        # Check the cache first if the track is there. If found and the service is YTMusic,
        # use the URL directly to download the track...
        target_query = ""
        cached_data = get_cached_result(normalized_service, track_id)
        if normalized_service == "ytmusic" and track_id and cached_data:
            target_query = cached_data.get("url")

        # Cache not found or it not from YTMusic, get artist & title from metdata retrieved above,
        # use it to search & download using yt-dlp ~
        if not target_query:
            artist_name = metadata.artists[0] if metadata.artists else "Unknown Artist"
            target_query = f"ytsearch1:{artist_name} - {metadata.title}"

        if auto_save:
            final_path = get_organized_library_path(
                str(data_dir), metadata, target_format
            )
            if final_path.exists():
                logger.info(
                    f"Track already exists in library, skipping download entirely."
                )
                return {"message": "Track is already in your library!"}, 200

        # Hash the query AND the target format! (same as album one above)
        query_hash = hashlib.md5(f"{target_query}:{target_format}".encode()).hexdigest()
        existing_files = list(temp_dir.glob(f"{query_hash}.*"))

        if existing_files:
            logger.info(f"Reusing existing temp file for: {target_query}")
            downloaded_path = existing_files[0]
            tag_audio_file(downloaded_path, metadata, overwrite=True)
            processed_items.append((downloaded_path, metadata))
        else:
            logger.info(f"Downloading via yt-dlp: {target_query}")
            ydl_opts["outtmpl"] = f"{query_hash}.%(ext)s"
            try:
                with YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                    error_code = ydl.download([target_query])
                    if error_code != 0:
                        return {"message": "Failed to download audio."}, 500
            except DownloadError as e:
                logger.error(f"yt-dlp DownloadError: {e}")
                return {"message": "Failed to download audio."}, 500
            except Exception as e:
                logger.exception(f"Unexpected error during yt-dlp download: {e}")
                return {"message": "An unexpected error occurred."}, 500

            downloaded_files = list(temp_dir.glob(f"{query_hash}.*"))
            if not downloaded_files:
                return {"message": "Download completed, but file was not found."}, 500

            downloaded_path = downloaded_files[0]
            tag_audio_file(downloaded_path, metadata, overwrite=True)
            processed_items.append((downloaded_path, metadata))

    # FINAL SAVE OR SEND TO BROWSER STEP !!!!!!!!!!!!!! We use `processed_items` list from above (which contain full path to downloaded files & metadata for each file as tuple) ~
    # ----------------------------------
    if auto_save:
        saved_count = 0
        skipped_count = 0

        for file_path, item_metadata in processed_items:
            actual_ext = file_path.suffix.lstrip(".")
            final_path = get_organized_library_path(
                str(data_dir), item_metadata, actual_ext
            )

            if final_path.exists():
                skipped_count += 1
                file_path.unlink(missing_ok=True)
                continue

            final_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.rename(final_path)
            logger.info(f"Saved to organized library: {final_path}")
            saved_count += 1

        if saved_count == 0 and skipped_count > 0:
            return {"message": "All tracks are already in your library!"}, 200

        return {
            "message": f"Successfully saved {saved_count} track(s) to library! ({skipped_count} skipped)",
        }, 200
    else:
        if len(processed_items) == 1:
            file_path, item_metadata = processed_items[0]
            actual_ext = file_path.suffix.lstrip(".")
            artist = (
                item_metadata.artists[0] if item_metadata.artists else "Unknown Artist"
            )
            title = item_metadata.title or "Unknown Title"
            download_name = sanitize_filename(f"{artist} - {title}.{actual_ext}")

            return send_file(
                file_path,
                as_attachment=True,
                download_name=download_name,
                mimetype=f"audio/{actual_ext}" if actual_ext != "mp3" else "audio/mpeg",
            )
        else:
            # Zip multiple files for browser download
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_path, item_metadata in processed_items:
                    actual_ext = file_path.suffix.lstrip(".")
                    safe_name = sanitize_filename(
                        generate_filename(item_metadata, actual_ext)
                    )
                    zip_file.write(file_path, arcname=safe_name)

            # Rewind the virtual file cursor back to the very beginning (0)!
            # After writing the zip, the "reading cursor" is at the end.
            # If me not rewind it, send_file will think the file is empty and send nothing www
            zip_buffer.seek(0)

            # Get artist from metadata, or fallback to the first track's artist!
            zip_artist = "Unknown Artist"
            if metadata.artists and len(metadata.artists) > 0:
                zip_artist = metadata.artists[0]
            elif processed_items and processed_items[0][1].artists:
                zip_artist = processed_items[0][1].artists[0]

            album_title = metadata.album or "Unknown Album"
            album_safe_name = sanitize_filename(f"{zip_artist} - {album_title}.zip")

            return send_file(
                zip_buffer,
                as_attachment=True,
                download_name=album_safe_name,
                mimetype="application/zip",
            )

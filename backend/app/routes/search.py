from urllib.parse import parse_qs, urlparse

from flask import Blueprint, request
from yutipy.deezer import Deezer
from yutipy.itunes import Itunes
from yutipy.musicyt import MusicYT

from app.logger import logger
from app.utils import get_current_settings

bp = Blueprint("search", __name__, url_prefix="/api")


@bp.route("/search", methods=["POST"])
def search():
    if not request.is_json:
        return {"message": "Missing JSON in request"}, 400

    data = request.get_json()
    settings = get_current_settings()

    search_method = data.get("search_method")
    artist = data.get("artist")
    song = data.get("song")
    url = data.get("music_url")

    if search_method == "named_search":
        return named_search(
            artist,
            song,
            settings,
        )
    elif search_method == "url_search":
        return url_search(
            url,
            settings,
        )
    else:
        return {"message": "Invalid search method"}, 400


# Helper functions ~
def named_search(artist: str, song: str, settings: dict):
    if not artist and not song:
        return {
            "message": "Please provide an Artist name, a Song title, or both. At least one field is required."
        }, 400

    results = {"albums": [], "artists": [], "tracks": []}

    # Try Deezer
    try:
        with Deezer() as deezer:
            result = deezer.search(artist=artist, song=song)
            if result:
                results["albums"] += result.get("albums", [])
                results["artists"] += result.get("artists", [])
                results["tracks"] += result.get("tracks", [])
    except Exception:
        logger.exception(
            "Deezer search failed for artist: %s, song: %s",
            artist,
            song,
        )

    # Try Itunes
    try:
        with Itunes(
            language=settings.get("language", "en"),
            location=settings.get("location", "US"),
        ) as itunes:
            result = itunes.search(
                artist=artist,
                song=song,
            )
            if result:
                results["albums"] += result.get("albums", [])
                results["artists"] += result.get("artists", [])
                results["tracks"] += result.get("tracks", [])
    except Exception:
        logger.exception(
            "Apple Music search failed for artist: %s, song: %s",
            artist,
            song,
        )

    # Try MusicYT
    try:
        with MusicYT(
            language=settings.get("language", "en"),
            location=settings.get("location", "US"),
        ) as yt_music:
            result = yt_music.search(artist=artist, song=song)
            print(result)
            if result:
                results["albums"] += result.get("albums", [])
                results["artists"] += result.get("artists", [])
                results["tracks"] += result.get("tracks", [])
    except Exception:
        logger.exception(
            "YouTube Music search failed for artist: %s, song: %s",
            artist,
            song,
        )

    # Check if we got absolutely nothing
    if not any(results.values()):
        return {"message": "No results found or all services failed."}, 404

    return {"results": results}


def url_search(url: str, settings: dict):
    if not url:
        return {"message": "Please provide a valid music URL."}, 400

    results = {"albums": [], "artists": [], "tracks": []}

    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    path_parts = [p for p in parsed.path.split("/") if p]
    query_params = parse_qs(parsed.query)

    try:
        # --- DEEZER ---
        if "deezer.com" in domain:
            # path_parts looks like ['us', 'track', '3066665361']
            if len(path_parts) >= 3:
                resource_type = path_parts[1]
                resource_id = path_parts[2]

                with Deezer() as deezer:
                    if resource_type == "track":
                        track = deezer.get_track(int(resource_id))
                        if track:
                            results["tracks"].append(track)
                    elif resource_type == "album":
                        album = deezer.get_album(int(resource_id))
                        if album:
                            results["albums"].append(album)

        # --- YOUTUBE MUSIC ---
        elif "youtube.com" in domain:
            resource_id = None
            resource_type = None

            # Check query parameters for tracks and some albums
            if "v" in query_params:
                resource_id = query_params["v"][0]
                resource_type = "track"
            elif "list" in query_params:
                resource_id = query_params["list"][0]
                resource_type = "album"
            # Check path for the v2 album link
            elif len(path_parts) >= 2 and path_parts[0] == "browse":
                resource_id = path_parts[1]
                resource_type = "album"

            if resource_id:
                with MusicYT(
                    language=settings.get("language", "en"),
                    location=settings.get("location", "US"),
                ) as yt_music:
                    if resource_type == "track":
                        track = yt_music.get_track(resource_id)
                        if track:
                            results["tracks"].append(track)
                    elif resource_type == "album":
                        album = yt_music.get_album(resource_id)
                        if album:
                            results["albums"].append(album)
        else:
            return {"message": "Unsupported music service URL."}, 400

    except Exception:
        logger.exception(
            "URL search failed for artist: %s, song: %s",
            url,
        )
        return {"message": "Something went wrong while searching for music!"}, 500

    return {"results": results}

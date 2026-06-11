from dataclasses import asdict

from flask import Blueprint, request
from yutipy.deezer import Deezer

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/search", methods=["POST"])
def search():
    if not request.is_json:
        return {"message": "Missing JSON in request"}, 400

    data = request.get_json()

    search_method = data.get("search_method")
    artist = data.get("artist")
    song = data.get("song")
    url = data.get("music_url")

    if not artist and not song:
        return {
            "message": "Please enter an Artist name, a Song title, or both. At least one field is required."
        }, 400

    results = {"albums": [], "artists": [], "tracks": []}
    try:
        with Deezer() as deezer:
            result = deezer.search(
                artist=artist,
                song=song,
            )
            results["albums"] += result["albums"] if result else []
            results["artists"] += result["artists"] if result else []
            results["tracks"] += result["tracks"] if result else []
    except Exception:
        return {"message": "Something went wrong while searching for music!"}, 500
    else:
        return {"results": results}

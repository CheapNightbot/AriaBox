import hashlib
import subprocess
from pathlib import Path
from typing import TypedDict

from flask import Blueprint, current_app, request, send_file

from app.logger import logger
from app.tagger import embed_cover_only, extract_cover_art
from app.utils import ALLOWED_EXTENSIONS, allowed_file

bp = Blueprint("convert", __name__, url_prefix="/api")

FFMPEG_TIMEOUT_SECONDS = 300


class ConversionProfile(TypedDict):
    codec: str
    args: list[str]


CONVERSION_PROFILES: dict[str, ConversionProfile] = {
    "mp3": {"codec": "libmp3lame", "args": ["-q:a", "2"]},
    "flac": {"codec": "flac", "args": []},
    "opus": {"codec": "libopus", "args": ["-b:a", "192k"]},
    "ogg": {"codec": "libopus", "args": ["-b:a", "192k"]},
    "m4a": {"codec": "aac", "args": ["-b:a", "256k"]},
    "wav": {"codec": "pcm_s16le", "args": []},
}


@bp.route("/convert", methods=["POST"])
def convert_audio():
    if "file" not in request.files:
        return {"message": "No file part in the request!"}, 400

    file = request.files["file"]
    if not file.filename:
        return {"message": "No file selected!"}, 400

    if not allowed_file(file.filename):
        return {
            "message": (
                "File type not allowed. Please upload one of: "
                f"{', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        }, 400

    target_format = request.form.get("format", "mp3").lower()
    if target_format not in CONVERSION_PROFILES:
        return {"message": "Unsupported target format!"}, 400

    data_dir = current_app.config.get("DATA_DIR")
    if not data_dir:
        return {"message": "Server configuration error."}, 500

    temp_dir = Path(data_dir) / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    max_file_size = current_app.config.get("MAX_AUDIO_FILE_BYTES", 100 * 1024 * 1024)

    # Calculate SHA-256 and enforce the per-file size limit.
    file_hash = hashlib.sha256()
    file_size = 0

    for chunk in iter(lambda: file.stream.read(8192), b""):
        file_size += len(chunk)
        if file_size > max_file_size:
            return {
                "message": (
                    "This file is too large. Please choose an audio file "
                    "no larger than 100 MiB (about 105 MB)."
                )
            }, 413
        file_hash.update(chunk)

    file_id = file_hash.hexdigest()
    file.stream.seek(0)

    original_filename = file.filename
    ext = Path(original_filename).suffix.lower()

    safe_input_name = f"{file_id}_in{ext}"
    input_path = temp_dir / safe_input_name

    profile = CONVERSION_PROFILES[target_format]
    safe_output_name = f"{file_id}_out.{target_format}"
    output_path = temp_dir / safe_output_name

    # Deduplication: if output already exists, just return it!
    if output_path.exists():
        logger.info(
            "Duplicate conversion detected! Returning existing file: %s",
            safe_output_name,
        )
    else:
        # Save the uploaded file.
        file.save(input_path)

        # Define ffmpeg command & args.
        cmd: list[str] = [
            "ffmpeg",
            "-i",
            str(input_path.resolve()),
            "-vn",
            "-c:a",
            profile["codec"],
            *profile["args"],
            str(output_path.resolve()),
            "-y",
        ]

        logger.info("Running conversion: %s", " ".join(cmd))

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=FFMPEG_TIMEOUT_SECONDS,
            )
        except FileNotFoundError:
            logger.error("FFmpeg is not installed or not found in the system PATH.")
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
            return {
                "message": (
                    "Audio conversion is currently unavailable. Please try again later."
                )
            }, 500
        except subprocess.TimeoutExpired:
            logger.warning(
                "FFmpeg conversion exceeded the %s-second timeout.",
                FFMPEG_TIMEOUT_SECONDS,
            )
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
            return {
                "message": (
                    "Audio conversion took too long and was stopped. "
                    "Try a shorter or smaller audio file."
                )
            }, 504
        except subprocess.CalledProcessError as e:
            logger.error("FFmpeg conversion failed: %s", e.stderr)
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
            return {
                "message": (
                    "Conversion failed. The file may be corrupted or unsupported."
                )
            }, 500

        try:
            cover_result = extract_cover_art(input_path)
            if cover_result:
                cover_data, mime_type = cover_result
                # This will crop it to a square and embed it perfectly!
                embed_cover_only(output_path, cover_data, mime_type)
        finally:
            # Clean up input file.
            input_path.unlink(missing_ok=True)

    # Send the converted file.
    download_name = f"{Path(original_filename).stem}.{target_format}"

    return send_file(
        str(output_path.resolve()),
        as_attachment=True,
        download_name=download_name,
        mimetype=f"audio/{target_format}" if target_format != "mp3" else "audio/mpeg",
    )

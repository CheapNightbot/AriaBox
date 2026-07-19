"""
The Tagger Module - Handles writing metadata to audio files.
"""

import base64
from pathlib import Path
from typing import Optional

import requests
from app.logger import logger
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, COMM, ID3, TALB, TBPM, TDRC, TIT2, TPE1, TPOS, TPUB, TRCK
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis


class Metadata:
    """Container for all the metadata we want to write."""

    def __init__(
        self,
        title: str,
        artists: list[str],
        album: Optional[str] = None,
        track_number: Optional[int] = None,
        total_tracks: Optional[int] = None,
        disc_number: Optional[int] = None,
        cover_url: Optional[str] = None,
        genre: Optional[str] = None,
        release_date: Optional[str] = None,
        label: Optional[str] = None,
        bpm: Optional[float] = None,
        isrc: Optional[str] = None,
    ):
        self.title = title
        self.artists = artists
        self.album = album
        self.track_number = track_number
        self.total_tracks = total_tracks
        self.disc_number = disc_number
        self.cover_url = cover_url
        self.genre = genre
        self.release_date = release_date
        self.label = label
        self.bpm = bpm
        self.isrc = isrc

    @classmethod
    def from_track(cls, track) -> "Metadata":
        """Create Metadata from a yutipy Track object."""
        return cls(
            title=track.title or "Unknown Title",
            artists=[a.name for a in (track.artists or []) if a.name],
            album=track.album.title if track.album else None,
            track_number=track.track_number,
            total_tracks=track.album.total_tracks if track.album else None,
            cover_url=track.album.cover if track.album else None,
            genre=track.genre,
            release_date=track.release_date,
            bpm=track.bpm,
            isrc=track.isrc,
        )

    @classmethod
    def from_album(cls, album) -> "Metadata":
        """Create Metadata from a yutipy Album object."""
        return cls(
            title=album.title or "Unknown Album",
            artists=[a.name for a in (album.artists or []) if a.name],
            album=album.title,
            total_tracks=album.total_tracks,
            cover_url=album.cover,
            genre=album.genres[0] if album.genres else None,
            release_date=album.release_date,
            label=album.label,
        )


def _download_cover(url: str) -> Optional[tuple[bytes, str]]:
    """
    Download cover art and guess MIME type from URL.
    Returns (bytes, mime_type) or None if download fails.
    """
    if not url:
        return None

    try:
        # Make a HEAD request first (this only downloads the headers, NOT the file!)
        head_response = requests.head(url, timeout=5, allow_redirects=True)
        content_type = head_response.headers.get("Content-Type", "").lower()

        # Check if the server claims it is an image
        if not content_type.startswith("image/"):
            logger.warning(f"URL does not point to an image: {content_type}")
            return None

        # If it is an image, THEN download it
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image_data = response.content

        # Use the actual Content-Type from the server, or fallback
        mime_type = (
            content_type
            if content_type in ["image/jpeg", "image/png", "image/webp"]
            else "image/jpeg"
        )

        logger.info(f"Downloaded cover art: {mime_type} ({len(image_data)} bytes)")
        return image_data, mime_type

    except Exception as e:
        logger.warning(f"Failed to download cover art from {url}: {e}")
        return None


def _tag_mp3(
    file_path: Path,
    metadata: Metadata,
    cover_data: Optional[bytes],
    mime_type: str,
    overwrite: bool = True,
):
    """Tag an MP3 file using ID3 tags."""
    audio = MP3(file_path, ID3=ID3)

    if overwrite:
        # DELETE old tags first!
        audio.delete()
        audio.tags = None

    # Add a fresh tag block if it doesn't exist
    if audio.tags is None:
        audio.add_tags()

    # Tell type checker that audio.tags is definitely not None now
    assert audio.tags is not None
    tags = audio.tags

    tags.add(TIT2(encoding=3, text=metadata.title))
    tags.add(TPE1(encoding=3, text=", ".join(metadata.artists)))

    if metadata.album:
        tags.add(TALB(encoding=3, text=metadata.album))

    if metadata.track_number:
        track_str = str(metadata.track_number)
        if metadata.total_tracks:
            track_str += f"/{metadata.total_tracks}"
        tags.add(TRCK(encoding=3, text=track_str))

    if metadata.disc_number:
        tags.add(TPOS(encoding=3, text=str(metadata.disc_number)))

    if metadata.bpm:
        tags.add(TBPM(encoding=3, text=str(int(metadata.bpm))))

    if metadata.release_date:
        tags.add(TDRC(encoding=3, text=metadata.release_date))

    if metadata.label:
        tags.add(TPUB(encoding=3, text=metadata.label))

    if metadata.isrc:
        tags.add(COMM(encoding=3, lang="eng", desc="ISRC", text=metadata.isrc))

    if cover_data:
        tags.add(
            APIC(
                encoding=3,
                mime=mime_type,
                type=3,
                desc="Cover",
                data=cover_data,
            )
        )

    audio.save()


def _tag_flac(
    file_path: Path,
    metadata: Metadata,
    cover_data: Optional[bytes],
    mime_type: str,
    overwrite: bool = True,
):
    """Tag a FLAC file using Vorbis comments."""
    audio = FLAC(file_path)

    if overwrite:
        # DELETE old tags first!
        audio.delete()

    audio["title"] = metadata.title
    audio["artist"] = ", ".join(metadata.artists)

    if metadata.album:
        audio["album"] = metadata.album

    if metadata.track_number:
        audio["tracknumber"] = str(metadata.track_number)

    if metadata.total_tracks:
        audio["tracktotal"] = str(metadata.total_tracks)

    if metadata.disc_number:
        audio["discnumber"] = str(metadata.disc_number)

    if metadata.genre:
        audio["genre"] = metadata.genre

    if metadata.release_date:
        audio["date"] = metadata.release_date

    if metadata.label:
        audio["label"] = metadata.label

    if metadata.bpm:
        audio["bpm"] = str(int(metadata.bpm))

    if metadata.isrc:
        audio["isrc"] = metadata.isrc

    if cover_data:
        picture = Picture()
        picture.type = 3
        picture.mime = mime_type
        picture.desc = "Cover"
        picture.data = cover_data
        audio.add_picture(picture)

    audio.save()


def _tag_mp4(
    file_path: Path,
    metadata: Metadata,
    cover_data: Optional[bytes],
    mime_type: str,
    overwrite: bool = True,
):
    """Tag an M4A/MP4 file using MP4 tags."""
    audio = MP4(file_path)

    if overwrite:
        # DELETE old tags first!
        audio.delete()

    audio["©nam"] = [metadata.title]
    audio["©ART"] = [", ".join(metadata.artists)]

    if metadata.album:
        audio["©alb"] = [metadata.album]

    if metadata.track_number:
        if metadata.total_tracks:
            audio["trkn"] = [(metadata.track_number, metadata.total_tracks)]
        else:
            audio["trkn"] = [(metadata.track_number, 0)]

    if metadata.genre:
        audio["©gen"] = [metadata.genre]

    if metadata.release_date:
        audio["©day"] = [metadata.release_date]

    if cover_data:
        if mime_type == "image/png":
            image_format = MP4Cover.FORMAT_PNG
        else:
            image_format = MP4Cover.FORMAT_JPEG

        audio["covr"] = [MP4Cover(cover_data, imageformat=image_format)]

    audio.save()


def _tag_ogg(
    file_path: Path,
    metadata: Metadata,
    cover_data: Optional[bytes],
    mime_type: str,
    overwrite: bool = True,
):
    """Tag an OGG Vorbis file."""
    audio = OggVorbis(file_path)

    if overwrite:
        # DELETE old tags first!
        audio.delete()

    audio["title"] = metadata.title
    audio["artist"] = ", ".join(metadata.artists)

    if metadata.album:
        audio["album"] = metadata.album

    if metadata.track_number:
        audio["tracknumber"] = str(metadata.track_number)

    if metadata.total_tracks:
        audio["tracktotal"] = str(metadata.total_tracks)

    if metadata.genre:
        audio["genre"] = metadata.genre

    if metadata.release_date:
        audio["date"] = metadata.release_date

    if metadata.bpm:
        audio["bpm"] = str(int(metadata.bpm))

    if cover_data:
        # https://mutagen.readthedocs.io/en/latest/user/vcomment.html
        try:
            picture = Picture()
            picture.data = cover_data
            picture.type = 3  # 3 = Cover (front)
            picture.desc = "Cover"
            picture.mime = mime_type

            # Note: width, height, and depth are optional.
            # Mutagen handles 0 gracefully if we don't know the image dimensions.
            picture.width = 0
            picture.height = 0
            picture.depth = 0

            # Write the picture to binary, then base64 encode it
            picture_data = picture.write()
            encoded_data = base64.b64encode(picture_data)
            vcomment_value = encoded_data.decode("ascii")

            # Assign to the special OGG Vorbis key
            audio["metadata_block_picture"] = [vcomment_value]
            logger.info("Successfully embedded cover art in OGG Vorbis file.")

        except Exception as e:
            logger.warning(f"Failed to embed cover art in OGG Vorbis: {e}")

    audio.save()


def tag_audio_file(file_path: Path, metadata: Metadata, overwrite: bool = True) -> bool:
    """
    Main function! Tags an audio file with metadata.

    Args:
        file_path: Path to the audio file
        metadata: Metadata object with the tags to write
        overwrite: If True, delete existing tags first. If False, keep existing tags.

    Returns True if successful, False otherwise.
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False

    # Download cover art (no validation, just guess MIME type)
    cover_result = _download_cover(metadata.cover_url) if metadata.cover_url else None
    cover_data = cover_result[0] if cover_result else None
    mime_type = cover_result[1] if cover_result else "image/jpeg"

    # Detect format by extension
    ext = file_path.suffix.lower()

    try:
        if ext == ".mp3":
            _tag_mp3(file_path, metadata, cover_data, mime_type, overwrite)
        elif ext == ".flac":
            _tag_flac(file_path, metadata, cover_data, mime_type, overwrite)
        elif ext in {".m4a", ".mp4", ".aac"}:
            _tag_mp4(file_path, metadata, cover_data, mime_type, overwrite)
        elif ext in {".ogg", ".opus"}:
            _tag_ogg(file_path, metadata, cover_data, mime_type, overwrite)
        else:
            logger.error(f"Unsupported audio format: {ext}")
            return False

        mode_str = "overwritten" if overwrite else "appended"
        logger.info(
            f"Successfully tagged {file_path.name} with metadata ({mode_str} mode)!"
        )
        return True

    except Exception as e:
        logger.exception(f"Failed to tag {file_path.name}: {e}")
        return False

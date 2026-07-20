"""
The Tagger Module - Handles writing metadata to audio files.
"""

import base64
import io
from pathlib import Path
from typing import Optional

import requests
from app.logger import logger
from mutagen import File as MutagenFile
from mutagen.flac import FLAC, Picture
from mutagen.id3 import (
    APIC,
    COMM,
    ID3,
    TALB,
    TBPM,
    TCOM,
    TDRC,
    TIT2,
    TPE1,
    TPE2,
    TPOS,
    TPUB,
    TRCK,
)
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from PIL import Image


class Metadata:
    """Container for all the metadata we want to write."""

    def __init__(
        self,
        title: str,
        artists: list[str],
        album: Optional[str] = None,
        album_artist: Optional[str] = None,
        track_number: Optional[int] = None,
        total_tracks: Optional[int] = None,
        disc_number: Optional[int] = None,
        total_discs: Optional[int] = None,
        cover_url: Optional[str] = None,
        genre: Optional[str] = None,
        release_date: Optional[str] = None,
        label: Optional[str] = None,
        bpm: Optional[float] = None,
        isrc: Optional[str] = None,
        composer: Optional[str] = None,
        comment: Optional[str] = None,
    ):
        self.title = title
        self.artists = artists
        self.album = album
        self.album_artist = album_artist
        self.track_number = track_number
        self.total_tracks = total_tracks
        self.disc_number = disc_number
        self.total_discs = total_discs
        self.cover_url = cover_url
        self.genre = genre
        self.release_date = release_date
        self.label = label
        self.bpm = bpm
        self.isrc = isrc
        self.composer = composer
        self.comment = comment

    @classmethod
    def from_track(cls, track) -> "Metadata":
        """Create Metadata from a yutipy Track object."""
        album_artist = None
        if track.album and track.album.artists and len(track.album.artists) > 0:
            first_album_artist = track.album.artists[0]
            if first_album_artist and first_album_artist.name:
                album_artist = first_album_artist.name

        return cls(
            title=track.title or "Unknown Title",
            artists=[a.name for a in (track.artists or []) if a and a.name],
            album=track.album.title if track.album else None,
            album_artist=album_artist,
            track_number=track.track_number,
            total_tracks=track.album.total_tracks if track.album else None,
            disc_number=getattr(track, "disc_number", None),
            cover_url=track.album.cover if track.album else None,
            genre=track.genre,
            release_date=track.release_date,
            label=getattr(track, "label", None),
            bpm=track.bpm,
            isrc=track.isrc,
            composer=getattr(track, "composer", None),
            comment=getattr(track, "comment", None),
        )

    @classmethod
    def from_album(cls, album) -> "Metadata":
        """Create Metadata from a yutipy Album object."""
        album_artist = None
        if album.artists and len(album.artists) > 0:
            first_album_artist = album.artists[0]
            if first_album_artist and first_album_artist.name:
                album_artist = first_album_artist.name

        return cls(
            title=album.title or "Unknown Album",
            artists=[a.name for a in (album.artists or []) if a and a.name],
            album_artist=album_artist,
            album=album.title,
            total_tracks=album.total_tracks,
            cover_url=album.cover,
            genre=album.genres[0] if album.genres else None,
            release_date=album.release_date,
            label=album.label,
        )


def _download_cover(url: str) -> Optional[tuple[bytes, str]]:
    """
    Download cover art and validate it using Pillow.
    Returns (bytes, mime_type) or None if download fails.
    """
    if not url:
        return None

    try:
        # Make a HEAD request first (security: check headers without downloading)
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

        # Validate it's actually a valid image using Pillow!
        try:
            img = Image.open(io.BytesIO(image_data))
            img.verify()  # Verify it's a valid image

            # Re-open to get format (verify() corrupts the image object)
            img = Image.open(io.BytesIO(image_data))

            # Determine the actual MIME type from the image format
            format_map = {
                "JPEG": "image/jpeg",
                "PNG": "image/png",
                "WEBP": "image/webp",
                "GIF": "image/gif",
            }
            mime_type = format_map.get(img.format or "JPEG", "image/jpeg")

            logger.info(
                f"Downloaded and validated cover art: {mime_type} ({len(image_data)} bytes)"
            )
            return image_data, mime_type

        except Exception as e:
            logger.warning(f"Downloaded file is not a valid image: {e}")
            return None

    except Exception as e:
        logger.warning(f"Failed to download cover art from {url}: {e}")
        return None


def _crop_cover_to_square(cover_data: bytes) -> bytes:
    """
    Crop cover art to 1:1 square ratio using Pillow.
    Returns the cropped image data, or the original if it fails.
    """
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(cover_data))
        width, height = img.size

        # Calculate the center square crop box
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2

        # Crop the image
        img_cropped = img.crop((left, top, right, bottom))

        # Save back to bytes (preserve original format, default to JPEG)
        output = io.BytesIO()
        img_format = img.format or "JPEG"
        img_cropped.save(output, format=img_format)
        return output.getvalue()

    except Exception as e:
        logger.warning(f"Failed to crop cover art: {e}")
        return cover_data  # Safe fallback to original


def extract_cover_art(file_path: Path) -> Optional[tuple[bytes, str]]:
    """Extract cover art from an audio file if it exists."""
    ext = file_path.suffix.lower()
    try:
        if ext in {".mp3", ".wav"}:
            audio = MP3(file_path, ID3=ID3)
            if audio.tags:
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        return tag.data, tag.mime  # type: ignore

        elif ext == ".flac":
            audio = FLAC(file_path)
            if audio.pictures:
                pic = audio.pictures[0]
                return pic.data, pic.mime

        elif ext in {".m4a", ".mp4", ".aac"}:
            audio = MP4(file_path)
            if "covr" in audio and len(audio["covr"]) > 0:
                cover = audio["covr"][0]
                mime = (
                    "image/png"
                    if cover.imageformat == MP4Cover.FORMAT_PNG
                    else "image/jpeg"
                )
                return bytes(cover), mime

        elif ext in {".ogg", ".opus"}:
            # AUTO-DETECT: Works perfectly for both .ogg (Vorbis) and .opus streams!
            audio = MutagenFile(str(file_path))
            if audio and "metadata_block_picture" in audio:
                b64_data = audio["metadata_block_picture"][0]
                pic_data = base64.b64decode(b64_data)
                pic = Picture(pic_data)
                return pic.data, pic.mime

    except Exception as e:
        logger.warning(f"Failed to extract cover art from {file_path}: {e}")

    return None


def embed_cover_only(file_path: Path, cover_data: bytes, mime_type: str) -> bool:
    """
    Embeds cover art into an existing file without touching text tags.
    Also crops the cover to a square first!
    """
    ext = file_path.suffix.lower()
    try:
        # Crop the cover art to square first!
        cropped_cover = _crop_cover_to_square(cover_data)

        if ext == ".mp3" or ext == ".wav":
            audio = MP3(file_path, ID3=ID3)
            if audio.tags is None:
                audio.add_tags()
            assert audio.tags is not None
            audio.tags.delall("APIC")
            audio.tags.add(
                APIC(
                    encoding=3, mime=mime_type, type=3, desc="Cover", data=cropped_cover
                )
            )
            audio.save()

        elif ext == ".flac":
            audio = FLAC(file_path)
            audio.clear_pictures()
            picture = Picture()
            picture.type = 3
            picture.mime = mime_type
            picture.desc = "Cover"
            picture.data = cropped_cover
            audio.add_picture(picture)
            audio.save()

        elif ext in {".m4a", ".mp4", ".aac"}:
            audio = MP4(file_path)
            image_format = (
                MP4Cover.FORMAT_PNG
                if mime_type == "image/png"
                else MP4Cover.FORMAT_JPEG
            )
            audio["covr"] = [MP4Cover(cropped_cover, imageformat=image_format)]
            audio.save()

        elif ext in {".ogg", ".opus"}:
            # AUTO-DETECT: Let mutagen figure out if it's Vorbis or Opus!
            audio = MutagenFile(str(file_path))

            # Fallback just in case auto-detect fails
            if audio is None:
                audio = OggOpus(file_path) if ext == ".opus" else OggVorbis(file_path)

            picture = Picture()
            picture.data = cropped_cover
            picture.type = 3
            picture.desc = "Cover"
            picture.mime = mime_type
            picture.width = 0
            picture.height = 0
            picture.depth = 0

            picture_data = picture.write()
            encoded_data = base64.b64encode(picture_data)
            audio["metadata_block_picture"] = [encoded_data.decode("ascii")]
            audio.save()

        else:
            return False

        logger.info(
            f"Successfully embedded (and cropped) cover art in {file_path.name}"
        )
        return True

    except Exception as e:
        logger.warning(f"Failed to embed cover art in {file_path}: {e}")
        return False


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
        audio.delete()
        audio.tags = None

    if audio.tags is None:
        audio.add_tags()

    assert audio.tags is not None
    tags = audio.tags

    # Basic info
    tags.add(TIT2(encoding=3, text=metadata.title))
    tags.add(TPE1(encoding=3, text=", ".join(metadata.artists)))

    if metadata.album:
        tags.add(TALB(encoding=3, text=metadata.album))

    if metadata.album_artist:
        tags.add(TPE2(encoding=3, text=metadata.album_artist))

    # Numbering
    if metadata.track_number:
        track_str = str(metadata.track_number)
        if metadata.total_tracks:
            track_str += f"/{metadata.total_tracks}"
        tags.add(TRCK(encoding=3, text=track_str))

    if metadata.disc_number:
        disc_str = str(metadata.disc_number)
        if metadata.total_discs:
            disc_str += f"/{metadata.total_discs}"
        tags.add(TPOS(encoding=3, text=disc_str))

    # Technical & Classification
    if metadata.bpm:
        tags.add(TBPM(encoding=3, text=str(int(metadata.bpm))))

    if metadata.release_date:
        tags.add(TDRC(encoding=3, text=metadata.release_date))

    if metadata.label:
        tags.add(TPUB(encoding=3, text=metadata.label))

    if metadata.isrc:
        tags.add(COMM(encoding=3, lang="eng", desc="ISRC", text=metadata.isrc))

    if metadata.genre:
        tags.add(COMM(encoding=3, lang="eng", desc="Genre", text=metadata.genre))

    if metadata.composer:
        tags.add(TCOM(encoding=3, text=metadata.composer))

    if metadata.comment:
        tags.add(COMM(encoding=3, lang="eng", desc="Comment", text=metadata.comment))

    # Cover art (cropped to square)
    if cover_data:
        cover_data = _crop_cover_to_square(cover_data)
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
        audio.delete()

    # Basic info
    audio["title"] = metadata.title
    audio["artist"] = ", ".join(metadata.artists)

    if metadata.album:
        audio["album"] = metadata.album

    if metadata.album_artist:
        audio["albumartist"] = metadata.album_artist

    # Numbering
    if metadata.track_number:
        audio["tracknumber"] = str(metadata.track_number)

    if metadata.total_tracks:
        audio["tracktotal"] = str(metadata.total_tracks)

    if metadata.disc_number:
        audio["discnumber"] = str(metadata.disc_number)

    if metadata.total_discs:
        audio["disctotal"] = str(metadata.total_discs)

    # Technical & Classification
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

    if metadata.composer:
        audio["composer"] = metadata.composer

    if metadata.comment:
        audio["comment"] = metadata.comment

    # Cover art (cropped to square)
    if cover_data:
        cover_data = _crop_cover_to_square(cover_data)
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
        audio.delete()

    # Basic info
    audio["©nam"] = [metadata.title]
    audio["©ART"] = [", ".join(metadata.artists)]

    if metadata.album:
        audio["©alb"] = [metadata.album]

    if metadata.album_artist:
        audio["aART"] = [metadata.album_artist]

    # Numbering
    if metadata.track_number:
        if metadata.total_tracks:
            audio["trkn"] = [(metadata.track_number, metadata.total_tracks)]
        else:
            audio["trkn"] = [(metadata.track_number, 0)]

    if metadata.disc_number:
        if metadata.total_discs:
            audio["disk"] = [(metadata.disc_number, metadata.total_discs)]
        else:
            audio["disk"] = [(metadata.disc_number, 0)]

    # Technical & Classification
    if metadata.genre:
        audio["©gen"] = [metadata.genre]

    if metadata.release_date:
        audio["©day"] = [metadata.release_date]

    if metadata.bpm:
        audio["tmpo"] = [int(metadata.bpm)]

    if metadata.composer:
        audio["©wrt"] = [metadata.composer]

    if metadata.comment:
        audio["©cmt"] = [metadata.comment]

    if metadata.isrc:
        audio["----:com.apple.iTunes:ISRC"] = [metadata.isrc]

    # Cover art (cropped to square)
    if cover_data:
        cover_data = _crop_cover_to_square(cover_data)
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
    """Tag an OGG Vorbis or Opus file."""
    # Auto-detect the file type based on its actual content, not just the extension!
    # This is crucial because ffmpeg might output an .ogg file containing an Opus stream.
    audio = MutagenFile(str(file_path))

    # Fallback: if mutagen couldn't identify it, try forcing based on extension
    if audio is None:
        ext = file_path.suffix.lower()
        if ext == ".opus":
            audio = OggOpus(file_path)
        else:
            audio = OggVorbis(file_path)

    # Safety check
    if audio is None:
        logger.error(f"Could not parse {file_path.name} as a valid Ogg/Opus file.")
        return

    if overwrite:
        audio.delete()

    # Basic info
    audio["title"] = metadata.title
    audio["artist"] = ", ".join(metadata.artists)

    if metadata.album:
        audio["album"] = metadata.album

    if metadata.album_artist:
        audio["albumartist"] = metadata.album_artist

    # Numbering
    if metadata.track_number:
        audio["tracknumber"] = str(metadata.track_number)

    if metadata.total_tracks:
        audio["tracktotal"] = str(metadata.total_tracks)

    if metadata.disc_number:
        audio["discnumber"] = str(metadata.disc_number)

    if metadata.total_discs:
        audio["disctotal"] = str(metadata.total_discs)

    # Technical & Classification
    if metadata.genre:
        audio["genre"] = metadata.genre

    if metadata.release_date:
        audio["date"] = metadata.release_date

    if metadata.bpm:
        audio["bpm"] = str(int(metadata.bpm))

    if metadata.isrc:
        audio["isrc"] = metadata.isrc

    if metadata.composer:
        audio["composer"] = metadata.composer

    if metadata.comment:
        audio["comment"] = metadata.comment

    if metadata.label:
        audio["label"] = metadata.label

    # Cover art (cropped to square)
    if cover_data:
        cover_data = _crop_cover_to_square(cover_data)
        try:
            # https://mutagen.readthedocs.io/en/latest/user/vcomment.html
            picture = Picture()
            picture.data = cover_data
            picture.type = 3
            picture.desc = "Cover"
            picture.mime = mime_type
            picture.width = 0
            picture.height = 0
            picture.depth = 0

            picture_data = picture.write()
            encoded_data = base64.b64encode(picture_data)
            vcomment_value = encoded_data.decode("ascii")

            audio["metadata_block_picture"] = [vcomment_value]
            logger.info(
                f"Successfully embedded cover art in {file_path.suffix.upper()} file."
            )

        except Exception as e:
            logger.warning(
                f"Failed to embed cover art in {file_path.suffix.upper()}: {e}"
            )

    audio.save()


def _tag_wav(
    file_path: Path,
    metadata: Metadata,
    overwrite: bool = True,
):
    """Tag a WAV file using ID3 tags."""
    audio = WAVE(file_path)

    if overwrite:
        audio.delete()
        audio.add_tags()
    elif audio.tags is None:
        audio.add_tags()

    assert audio.tags is not None
    tags = audio.tags

    # Basic info
    tags.add(TIT2(encoding=3, text=metadata.title))
    tags.add(TPE1(encoding=3, text=", ".join(metadata.artists)))

    if metadata.album:
        tags.add(TALB(encoding=3, text=metadata.album))

    if metadata.album_artist:
        tags.add(TPE2(encoding=3, text=metadata.album_artist))

    # Numbering
    if metadata.track_number:
        track_str = str(metadata.track_number)
        if metadata.total_tracks:
            track_str += f"/{metadata.total_tracks}"
        tags.add(TRCK(encoding=3, text=track_str))

    if metadata.disc_number:
        disc_str = str(metadata.disc_number)
        if metadata.total_discs:
            disc_str += f"/{metadata.total_discs}"
        tags.add(TPOS(encoding=3, text=disc_str))

    # Technical & Classification
    if metadata.bpm:
        tags.add(TBPM(encoding=3, text=str(int(metadata.bpm))))

    if metadata.release_date:
        tags.add(TDRC(encoding=3, text=metadata.release_date))

    if metadata.label:
        tags.add(TPUB(encoding=3, text=metadata.label))

    if metadata.isrc:
        tags.add(COMM(encoding=3, lang="eng", desc="ISRC", text=metadata.isrc))

    if metadata.genre:
        tags.add(COMM(encoding=3, lang="eng", desc="Genre", text=metadata.genre))

    if metadata.composer:
        tags.add(TCOM(encoding=3, text=metadata.composer))

    if metadata.comment:
        tags.add(COMM(encoding=3, lang="eng", desc="Comment", text=metadata.comment))

    # Note: Cover art in WAV is notoriously poorly supported by players,
    # so we skip it to avoid corrupting the RIFF header

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
        elif ext == ".wav":
            _tag_wav(file_path, metadata, overwrite)
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

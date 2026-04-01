import os
import shutil

from PIL import Image


def ensure_pillow_compat() -> None:
    if not hasattr(Image, "ANTIALIAS") and hasattr(Image, "Resampling"):
        Image.ANTIALIAS = Image.Resampling.LANCZOS


def ensure_ffmpeg() -> None:
    if os.getenv("FFMPEG_BINARY") and os.getenv("IMAGEIO_FFMPEG_EXE"):
        return

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        os.environ.setdefault("FFMPEG_BINARY", system_ffmpeg)
        os.environ.setdefault("IMAGEIO_FFMPEG_EXE", system_ffmpeg)
        return

    try:
        import imageio_ffmpeg

        bundled_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        os.environ.setdefault("FFMPEG_BINARY", bundled_ffmpeg)
        os.environ.setdefault("IMAGEIO_FFMPEG_EXE", bundled_ffmpeg)
    except Exception:
        os.environ.setdefault("FFMPEG_BINARY", "ffmpeg")

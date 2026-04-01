from .ffmpeg_setup import ensure_ffmpeg, ensure_pillow_compat

ensure_pillow_compat()
ensure_ffmpeg()

def generate_video(*args, **kwargs):
	from .main import generate_video as _generate_video

	return _generate_video(*args, **kwargs)


__all__ = ["generate_video", "ensure_ffmpeg"]

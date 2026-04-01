from pathlib import Path

from moviepy.editor import ImageClip
from PIL import Image, ImageDraw, ImageFont

from .utils import sentence_split


def _pick_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []

    for word in words:
        trial = " ".join(current + [word])
        box = draw.textbbox((0, 0), trial, font=font)
        width = box[2] - box[0]
        if width <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def _build_caption_image(text: str, size: tuple[int, int], place_top: bool, out_path: Path) -> None:
    width, height = size
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    font_size = max(34, int(width * 0.04))
    font = _pick_font(font_size)
    wrapped = _wrap_text(draw, text, font, max_width=int(width * 0.82))

    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=8, align="center")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    x = (width - tw) // 2
    if place_top:
        y = int(height * 0.1)
    else:
        y = int(height * 0.72)

    pad_x = int(width * 0.02)
    pad_y = int(height * 0.015)
    draw.rounded_rectangle(
        (x - pad_x, y - pad_y, x + tw + pad_x, y + th + pad_y),
        radius=16,
        fill=(0, 0, 0, 160),
    )
    draw.multiline_text((x, y), wrapped, font=font, fill=(255, 255, 255, 245), align="center", spacing=8)

    image.save(out_path)


def create_caption_clips(
    full_script: str,
    total_duration: float,
    output_dir: Path,
    frame_size: tuple[int, int] = (1920, 1080),
) -> list[ImageClip]:
    captions = sentence_split(full_script)
    if not captions:
        return []

    caption_dir = output_dir / "captions"
    caption_dir.mkdir(parents=True, exist_ok=True)

    words_total = max(1, len(full_script.split()))
    current_start = 0.0
    clips: list[ImageClip] = []

    for i, sentence in enumerate(captions):
        words = max(1, len(sentence.split()))
        duration = max(1.2, (words / words_total) * total_duration)
        if i == len(captions) - 1:
            duration = max(0.8, total_duration - current_start)

        start = current_start
        end = min(total_duration, start + duration)
        if end <= start:
            break

        img_path = caption_dir / f"caption_{i + 1}.png"
        _build_caption_image(sentence, frame_size, place_top=(i % 2 == 0), out_path=img_path)

        clip = ImageClip(str(img_path)).set_start(start).set_duration(end - start)
        clips.append(clip)
        current_start = end

    return clips

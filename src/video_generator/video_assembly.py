from pathlib import Path
from typing import Any

from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_audioclips,
    concatenate_videoclips,
)

from .models import ScriptData, ScriptSection


def _loop_clip(clip, target_duration: float):
    if clip.duration >= target_duration:
        return clip.subclip(0, target_duration)
    repeats = int(target_duration / clip.duration) + 1
    looped = concatenate_videoclips([clip] * repeats)
    return looped.subclip(0, target_duration)


def _loop_audio_clip(clip, target_duration: float):
    if clip.duration >= target_duration:
        return clip.subclip(0, target_duration)
    repeats = int(target_duration / clip.duration) + 1
    looped = concatenate_audioclips([clip] * repeats)
    return looped.subclip(0, target_duration)


def _to_1080p(clip):
    target_w, target_h = 1920, 1080
    src_w, src_h = clip.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h

    if src_ratio > target_ratio:
        clip = clip.resize(height=target_h)
        x1 = int((clip.w - target_w) / 2)
        clip = clip.crop(x1=x1, y1=0, x2=x1 + target_w, y2=target_h)
    else:
        clip = clip.resize(width=target_w)
        y1 = int((clip.h - target_h) / 2)
        clip = clip.crop(x1=0, y1=y1, x2=target_w, y2=y1 + target_h)

    return clip


def _build_visual_clip(asset: dict[str, Any], duration: float):
    path = asset["path"]
    media_type = asset.get("type", "image")

    if media_type == "video" and Path(path).suffix.lower() == ".mp4":
        clip = VideoFileClip(path)
        clip = _loop_clip(clip, duration)
    else:
        clip = ImageClip(path).set_duration(duration)

    return _to_1080p(clip).set_duration(duration)


def _section_durations(sections: list[ScriptSection], fallback_total: float) -> list[float]:
    values = []
    for i, section in enumerate(sections):
        if section.end > section.start:
            values.append(section.end - section.start)
        elif i < len(sections) - 1:
            values.append(max(0.5, sections[i + 1].start - section.start))
        else:
            values.append(max(0.5, fallback_total - section.start))

    total = sum(values)
    if total <= 0:
        each = fallback_total / max(1, len(sections))
        return [each] * len(sections)

    ratio = fallback_total / total
    return [max(0.6, v * ratio) for v in values]


def assemble_video(
    script: ScriptData,
    audio_path: str,
    assets: list[dict[str, Any]],
    caption_clips: list[ImageClip],
    output_path: str,
    background_music_path: str | None = None,
) -> str:
    if not assets:
        raise ValueError("No media assets available")

    with AudioFileClip(audio_path) as narration:
        total_duration = narration.duration
        durations = _section_durations(script.sections, total_duration)

        visual_parts = []
        for i, section in enumerate(script.sections):
            asset = assets[i % len(assets)]
            duration = durations[i]
            clip = _build_visual_clip(asset=asset, duration=duration)
            clip = clip.crossfadein(0.35).crossfadeout(0.35)
            visual_parts.append(clip)

        video_track = concatenate_videoclips(visual_parts, method="compose", padding=-0.2)
        video_track = video_track.set_duration(total_duration)

        layers = [video_track]
        layers.extend(caption_clips)
        final = CompositeVideoClip(layers, size=(1920, 1080))

        audio_layers = [narration]
        if background_music_path and Path(background_music_path).exists():
            bgm = AudioFileClip(background_music_path).volumex(0.08)
            bgm = _loop_audio_clip(bgm, total_duration)
            audio_layers.append(bgm)

        mix = CompositeAudioClip(audio_layers)
        final = final.set_audio(mix).set_duration(total_duration)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        final.write_videofile(
            output_path,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            preset="veryfast",
            threads=4,
        )

        final.close()
        video_track.close()
        for c in visual_parts:
            c.close()

    return output_path

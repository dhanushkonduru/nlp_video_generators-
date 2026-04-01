from datetime import datetime
from pathlib import Path

from .caption_generation import create_caption_clips
from .config import load_config
from .content_generation import generate_script
from .media_retrieval import retrieve_media
from .models import PipelineResult
from .speech_synthesis import synthesize_speech
from .utils import safe_filename, write_json
from .video_assembly import assemble_video


def generate_video(
    topic: str,
    audience: str,
    tone: str,
    duration_seconds: int,
    output_dir: str | None = None,
    background_music_path: str | None = None,
    tts_engine: str = "speecht5",
) -> PipelineResult:
    config = load_config(output_dir, tts_engine=tts_engine)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = safe_filename(topic)[:60]
    run_dir = Path(config.output_root) / f"{run_name}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    script = generate_script(topic, audience, tone, duration_seconds, config)
    script_json_path = run_dir / "script.json"
    write_json(
        script_json_path,
        {
            "sections": [
                {"text": s.text, "start": s.start, "end": s.end}
                for s in script.sections
            ],
            "full_script": script.full_script,
        },
    )

    audio_path, audio_duration = synthesize_speech(script, run_dir, engine=config.tts_engine)

    assets = retrieve_media(script, topic, config, run_dir)
    assets_json_path = run_dir / "assets_used.json"
    write_json(assets_json_path, assets)

    captions = create_caption_clips(
        full_script=script.full_script,
        total_duration=audio_duration,
        output_dir=run_dir,
        frame_size=(1920, 1080),
    )

    final_video_path = str(run_dir / "final_video.mp4")
    assemble_video(
        script=script,
        audio_path=audio_path,
        assets=assets,
        caption_clips=captions,
        output_path=final_video_path,
        background_music_path=background_music_path,
    )

    return PipelineResult(
        final_video_path=final_video_path,
        script_json_path=str(script_json_path),
        assets_json_path=str(assets_json_path),
        assets_used=assets,
    )

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    grok_api_key: str
    pexels_api_key: str
    output_root: Path
    fallback_media_count: int = 6
    grok_model: str = "grok-3-latest"
    tts_engine: str = "speecht5"


def load_config(output_dir: str | None = None, tts_engine: str = "speecht5") -> AppConfig:
    root = Path(output_dir or "outputs").resolve()
    root.mkdir(parents=True, exist_ok=True)
    return AppConfig(
        grok_api_key=os.getenv("GROK_API_KEY", "").strip(),
        pexels_api_key=os.getenv("PEXELS_API_KEY", "").strip(),
        output_root=root,
        tts_engine=tts_engine,
    )

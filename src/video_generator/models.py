from dataclasses import dataclass
from typing import Any


@dataclass
class ScriptSection:
    text: str
    start: float
    end: float


@dataclass
class ScriptData:
    sections: list[ScriptSection]
    full_script: str


@dataclass
class PipelineResult:
    final_video_path: str
    script_json_path: str
    assets_json_path: str
    assets_used: list[dict[str, Any]]

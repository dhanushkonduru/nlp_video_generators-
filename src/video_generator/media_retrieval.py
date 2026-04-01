import re
from pathlib import Path
from typing import Any

import requests
from PIL import Image, ImageDraw, ImageFont

from .config import AppConfig
from .models import ScriptData


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "for",
    "with",
    "is",
    "are",
    "this",
    "that",
    "it",
    "on",
    "as",
    "by",
    "from",
}


def _extract_keywords(text: str, max_terms: int = 4) -> str:
    tokens = re.findall(r"[a-zA-Z]{3,}", text.lower())
    picked: list[str] = []
    for token in tokens:
        if token in STOPWORDS:
            continue
        if token not in picked:
            picked.append(token)
        if len(picked) >= max_terms:
            break
    return " ".join(picked) if picked else text[:40]


def _download_file(url: str, target_path: Path) -> bool:
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with target_path.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception:
        return False


def _generate_fallback_assets(topic: str, out_dir: Path, count: int) -> list[dict[str, Any]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    generated: list[dict[str, Any]] = []
    font = ImageFont.load_default()

    for i in range(count):
        path = out_dir / f"fallback_{i + 1}.png"
        image = Image.new("RGB", (1920, 1080), color=(24 + i * 10, 50 + i * 6, 90 + i * 4))
        draw = ImageDraw.Draw(image)
        label = f"{topic}\nEducational Visual {i + 1}"
        bbox = draw.multiline_textbbox((0, 0), label, font=font, align="center")
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (1920 - tw) // 2
        y = (1080 - th) // 2
        draw.rectangle((x - 30, y - 20, x + tw + 30, y + th + 20), fill=(0, 0, 0, 150))
        draw.multiline_text((x, y), label, fill=(245, 245, 245), font=font, align="center")
        image.save(path)
        generated.append({"path": str(path), "source": "fallback", "type": "image"})

    return generated


def _fetch_pexels_videos(query: str, api_key: str, per_page: int = 3) -> list[dict[str, Any]]:
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": per_page, "orientation": "landscape"}
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("videos", [])


def retrieve_media(script: ScriptData, topic: str, config: AppConfig, output_dir: Path) -> list[dict[str, Any]]:
    media_dir = output_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    if not config.pexels_api_key:
        return _generate_fallback_assets(topic, media_dir, config.fallback_media_count)

    assets: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    queries = []
    for section in script.sections:
        query = _extract_keywords(section.text)
        if query not in queries:
            queries.append(query)
    if topic not in queries:
        queries.insert(0, topic)

    try:
        for query in queries[:8]:
            videos = _fetch_pexels_videos(query=query, api_key=config.pexels_api_key, per_page=3)
            for video in videos:
                if len(assets) >= 8:
                    break
                candidates = []
                for f in video.get("video_files", []):
                    width = int(f.get("width") or 0)
                    height = int(f.get("height") or 0)
                    if width < 1280 or height < 720 or width <= height:
                        continue
                    if "mp4" not in str(f.get("file_type", "")).lower():
                        continue
                    candidates.append(f)
                if not candidates:
                    continue
                candidates.sort(key=lambda x: int(x.get("width", 0)) * int(x.get("height", 0)), reverse=True)
                pick = candidates[0]
                src = pick.get("link")
                if not src or src in seen_urls:
                    continue
                seen_urls.add(src)
                local_path = media_dir / f"pexels_{len(assets) + 1}.mp4"
                if _download_file(src, local_path):
                    assets.append({"path": str(local_path), "source": "pexels", "type": "video", "query": query})
            if len(assets) >= 5:
                break
    except Exception:
        pass

    if len(assets) < 5:
        fallback = _generate_fallback_assets(topic, media_dir, max(5, config.fallback_media_count) - len(assets))
        assets.extend(fallback)

    return assets

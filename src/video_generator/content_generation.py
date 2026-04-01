import math
from typing import Any

import requests

from .config import AppConfig
from .models import ScriptData, ScriptSection
from .utils import clamp, extract_json


GROK_API_URL = "https://api.x.ai/v1/chat/completions"


def _fallback_script(topic: str, audience: str, tone: str, duration_seconds: int) -> ScriptData:
    hook_end = 5
    recap_start = max(duration_seconds - 5, 20)
    explain_end = max(hook_end + 8, recap_start - 10)

    hook = f"Did you know this about {topic}? Let us break it down quickly."
    explanation = (
        f"{topic} matters in everyday life. For {audience}, the core idea is simple. "
        f"Think of it as a system with causes and effects you can observe."
    )
    key_points = (
        f"Key point one: define {topic} clearly. "
        f"Key point two: explain how it works with one practical example. "
        f"Key point three: connect it to why people should care."
    )
    recap = f"Recap: {topic} is important, understandable, and useful when applied carefully."

    sections = [
        ScriptSection(text=hook, start=0, end=hook_end),
        ScriptSection(text=explanation, start=hook_end, end=explain_end),
        ScriptSection(text=key_points, start=explain_end, end=recap_start),
        ScriptSection(text=recap, start=recap_start, end=duration_seconds),
    ]
    full_script = " ".join(s.text for s in sections)
    return ScriptData(sections=sections, full_script=full_script)


def _normalize_script(raw: dict[str, Any], duration_seconds: int) -> ScriptData:
    sections_data = raw.get("sections", [])
    if not sections_data:
        raise ValueError("Script JSON missing sections")

    parsed_sections: list[ScriptSection] = []
    for section in sections_data:
        text = str(section.get("text", "")).strip()
        if not text:
            continue
        start = float(section.get("start", 0))
        end = float(section.get("end", 0))
        parsed_sections.append(ScriptSection(text=text, start=start, end=end))

    if not parsed_sections:
        raise ValueError("No valid script sections parsed")

    parsed_sections.sort(key=lambda s: s.start)

    for i, section in enumerate(parsed_sections):
        section.start = clamp(section.start, 0, duration_seconds)
        section.end = clamp(section.end, section.start + 0.5, duration_seconds)
        if i > 0 and section.start < parsed_sections[i - 1].end:
            section.start = parsed_sections[i - 1].end
            section.end = clamp(section.end, section.start + 0.5, duration_seconds)

    parsed_sections[0].start = 0
    parsed_sections[-1].end = duration_seconds

    full_script = str(raw.get("full_script", "")).strip()
    if not full_script:
        full_script = " ".join(s.text for s in parsed_sections)

    return ScriptData(sections=parsed_sections, full_script=full_script)


def _build_prompt(topic: str, audience: str, tone: str, duration_seconds: int, simplified: bool) -> str:
    base = (
        "Generate a factual educational narration script in JSON only. "
        "No markdown, no extra text. Keep sentences short."
    )
    details = (
        f"Topic: {topic}. Audience: {audience}. Tone: {tone}. "
        f"Target duration: {duration_seconds} seconds. "
        "Return JSON with keys sections and full_script. "
        "sections must have exactly 4 entries in this order: hook, explanation, key points, recap. "
        "Use timestamps with start and end in seconds. "
        "Hook covers first 5 seconds. Recap covers last 5 seconds. "
        "Key points section must use bullet-like narration with short clauses. "
        "Avoid uncertain claims. If a fact is uncertain, use conservative wording."
    )
    if simplified:
        details = (
            f"Topic: {topic}. Audience: {audience}. Duration: {duration_seconds}. "
            "Return valid JSON with sections and full_script only."
        )
    return f"{base} {details}"


def generate_script(
    topic: str,
    audience: str,
    tone: str,
    duration_seconds: int,
    config: AppConfig,
) -> ScriptData:
    duration_seconds = int(clamp(duration_seconds, 30, 60))
    if not config.grok_api_key:
        return _fallback_script(topic, audience, tone, duration_seconds)

    headers = {
        "Authorization": f"Bearer {config.grok_api_key}",
        "Content-Type": "application/json",
    }

    attempts = [False, False, True]
    for simplified in attempts:
        prompt = _build_prompt(topic, audience, tone, duration_seconds, simplified)
        payload = {
            "model": config.grok_model,
            "messages": [
                {"role": "system", "content": "You are a precise educational content writer."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        try:
            response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            raw = extract_json(content)
            script = _normalize_script(raw, duration_seconds)
            if len(script.full_script.split()) < math.ceil(duration_seconds * 1.8):
                continue
            return script
        except Exception:
            continue

    return _fallback_script(topic, audience, tone, duration_seconds)

from pathlib import Path
import os

import numpy as np
from moviepy.editor import AudioFileClip, concatenate_audioclips

from .models import ScriptData


# Set torch environment variables for macOS stability
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")


def _estimate_duration_seconds(text: str) -> float:
    words = max(1, len(text.split()))
    return words / 2.5


def _synthesize_with_speecht5(text: str, output_wav: Path) -> tuple[bool, float]:
    try:
        import torch
        import torchaudio
        from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech

        device = "mps" if torch.backends.mps.is_available() else "cpu"
        try:
            processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
            model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)
        except Exception as e:
            print(f"Failed to load SpeechT5 on {device}: {e}. Falling back to CPU...")
            device = "cpu"
            processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
            model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)

        speaker_embeddings = torch.randn(1, 512).to(device)

        inputs = processor(text=text, return_tensors="pt").to(device)
        with torch.no_grad():
            speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=None)

        sample_rate = 22050
        torchaudio.save(str(output_wav), speech.cpu(), sample_rate)

        duration = float(len(speech) / sample_rate)
        return True, duration
    except Exception as e:
        print(f"SpeechT5 failed: {e}")
        return False, 0.0


def _synthesize_with_gtts(text: str, output_wav: Path) -> tuple[bool, float]:
    try:
        from gtts import gTTS

        mp3_path = output_wav.parent / "narration_temp.mp3"
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(str(mp3_path))

        with AudioFileClip(str(mp3_path)) as audio:
            audio.write_audiofile(str(output_wav), fps=44100, verbose=False, logger=None)
            duration = float(audio.duration)

        mp3_path.unlink(missing_ok=True)
        return True, duration
    except Exception as e:
        print(f"gTTS failed: {e}")
        return False, 0.0


def synthesize_speech(script: ScriptData, output_dir: Path, engine: str = "speecht5") -> tuple[str, float]:
    output_dir.mkdir(parents=True, exist_ok=True)
    wav_path = output_dir / "narration.wav"

    text = script.full_script

    if engine == "speecht5":
        success, duration = _synthesize_with_speecht5(text, wav_path)
        if success:
            return str(wav_path), duration
        print("Falling back to gTTS...")
        success, duration = _synthesize_with_gtts(text, wav_path)
        if success:
            return str(wav_path), duration
    else:
        success, duration = _synthesize_with_gtts(text, wav_path)
        if success:
            return str(wav_path), duration
        print("Falling back to SpeechT5...")
        success, duration = _synthesize_with_speecht5(text, wav_path)
        if success:
            return str(wav_path), duration

    raise RuntimeError("All TTS engines failed. Check dependencies: pip install transformers torch torchaudio gtts")

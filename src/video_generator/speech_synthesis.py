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

        print("[SpeechT5] Initializing model...")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"[SpeechT5] Using device: {device}")
        
        try:
            print("[SpeechT5] Loading processor...")
            processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
            print("[SpeechT5] Loading model...")
            model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)
            print("[SpeechT5] Model loaded successfully")
        except Exception as e:
            print(f"[SpeechT5] Failed to load model on {device}: {e}. Falling back to CPU...")
            device = "cpu"
            processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
            model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)

        speaker_embeddings = torch.randn(1, 512).to(device)

        print(f"[SpeechT5] Processing text ({len(text)} chars)...")
        inputs = processor(text=text, return_tensors="pt").to(device)
        
        print("[SpeechT5] Generating speech...")
        with torch.no_grad():
            speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=None)

        print("[SpeechT5] Saving audio...")
        sample_rate = 22050
        torchaudio.save(str(output_wav), speech.cpu(), sample_rate)

        duration = float(len(speech) / sample_rate)
        print(f"[SpeechT5] Success! Duration: {duration:.1f}s")
        return True, duration
    except Exception as e:
        print(f"[SpeechT5] Failed: {type(e).__name__}: {e}")
        return False, 0.0


def _synthesize_with_gtts(text: str, output_wav: Path) -> tuple[bool, float]:
    try:
        from gtts import gTTS

        print("[gTTS] Generating speech from text...")
        mp3_path = output_wav.parent / "narration_temp.mp3"
        tts = gTTS(text=text, lang="en", slow=False)
        print("[gTTS] Saving to temporary MP3...")
        tts.save(str(mp3_path))

        print("[gTTS] Converting MP3 to WAV...")
        with AudioFileClip(str(mp3_path)) as audio:
            audio.write_audiofile(str(output_wav), fps=44100, verbose=False, logger=None)
            duration = float(audio.duration)

        print(f"[gTTS] Cleaning up and success! Duration: {duration:.1f}s")
        mp3_path.unlink(missing_ok=True)
        return True, duration
    except Exception as e:
        print(f"[gTTS] Failed: {type(e).__name__}: {e}")
        return False, 0.0


def synthesize_speech(script: ScriptData, output_dir: Path, engine: str = "speecht5") -> tuple[str, float]:
    output_dir.mkdir(parents=True, exist_ok=True)
    wav_path = output_dir / "narration.wav"

    text = script.full_script
    print(f"\n[Speech] Starting synthesis with engine='{engine}' ({len(text)} chars)")

    if engine == "speecht5":
        print("[Speech] Attempting SpeechT5 (high quality)...")
        success, duration = _synthesize_with_speecht5(text, wav_path)
        if success:
            print(f"[Speech] SpeechT5 succeeded!")
            return str(wav_path), duration
        print("[Speech] SpeechT5 failed, falling back to gTTS...")
        success, duration = _synthesize_with_gtts(text, wav_path)
        if success:
            print(f"[Speech] gTTS fallback succeeded!")
            return str(wav_path), duration
        raise RuntimeError("Both SpeechT5 and gTTS failed!")
    else:
        print("[Speech] Attempting gTTS (lightweight)...")
        success, duration = _synthesize_with_gtts(text, wav_path)
        if success:
            print(f"[Speech] gTTS succeeded!")
            return str(wav_path), duration
        print("[Speech] gTTS failed, falling back to SpeechT5...")
        success, duration = _synthesize_with_speecht5(text, wav_path)
        if success:
            print(f"[Speech] SpeechT5 fallback succeeded!")
            return str(wav_path), duration
        raise RuntimeError("Both gTTS and SpeechT5 failed!")

    raise RuntimeError("All TTS engines failed. Check dependencies: pip install transformers torch torchaudio gtts")

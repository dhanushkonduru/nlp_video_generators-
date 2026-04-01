import json
import os
import sys
import traceback
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Initialize environment variables before importing torch/transformers
load_dotenv(".env")
load_dotenv(".env.example")

# Set torch environment variables for macOS stability
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from src.video_generator.main import generate_video


def _load_json(path: str) -> dict | list:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _validate_config() -> tuple[bool, str]:
    """Validate API keys and configuration."""
    grok_key = os.getenv("GROK_API_KEY", "").strip()
    pexels_key = os.getenv("PEXELS_API_KEY", "").strip()
    
    issues = []
    if not grok_key or grok_key == "test_key" or grok_key.startswith("your_"):
        issues.append("GROK_API_KEY is not set or is a placeholder")
    if not pexels_key or pexels_key == "test_key" or pexels_key.startswith("your_"):
        issues.append("PEXELS_API_KEY is not set or is a placeholder")
    
    if issues:
        return False, " | ".join(issues)
    return True, "OK"


def main() -> None:
    st.set_page_config(page_title="AI Educational Video Generator", layout="wide")
    st.title("AI Educational Video Generator")
    st.caption("Create a 30-60 second educational video from a topic")
    
    # Check configuration on load
    valid, config_msg = _validate_config()
    if not valid:
        st.warning(f"⚠️ Configuration issue: {config_msg}\n\n1. Create `.env` file in project root\n2. Add your API keys from:\n   - Grok: https://console.x.ai/\n   - Pexels: https://www.pexels.com/api/\n3. Restart the app")

    with st.sidebar:
        st.header("Inputs")
        topic = st.text_input("Topic", value="The water cycle")
        audience = st.selectbox("Target audience", options=["kids", "students", "general"], index=1)
        tone = st.selectbox("Tone", options=["formal", "engaging", "storytelling"], index=1)
        duration = st.slider("Duration (seconds)", min_value=30, max_value=60, value=45, step=1)
        tts_engine = st.selectbox(
            "TTS Engine", 
            options=["gtts", "speecht5"], 
            index=0, 
            help="gTTS is more stable on macOS. SpeechT5 offers better quality but requires more resources."
        )
        output_dir = st.text_input("Output directory", value="outputs")
        bgm_path = st.text_input("Optional background music path", value="")
        generate = st.button("Generate Video", type="primary", disabled=not valid)

    if generate:
        if not topic.strip():
            st.error("Please enter a topic.")
            return

        with st.spinner("Generating video. This can take a few minutes..."):
            try:
                st.info(f"Using {tts_engine.upper()} engine for speech synthesis...")
                result = generate_video(
                    topic=topic.strip(),
                    audience=audience,
                    tone=tone,
                    duration_seconds=int(duration),
                    output_dir=output_dir.strip() or "outputs",
                    background_music_path=bgm_path.strip() or None,
                    tts_engine=tts_engine,
                )
            except KeyboardInterrupt:
                st.warning("Generation cancelled by user.")
                return
            except Exception as exc:
                error_msg = str(exc)
                st.error(f"❌ Generation failed: {error_msg}")
                
                # Provide specific troubleshooting
                if "GROK" in error_msg.upper() or "401" in error_msg:
                    st.warning("⚠️ API Authentication Error\n- Check your GROK_API_KEY is valid\n- Verify .env file exists and is readable")
                elif "PEXELS" in error_msg.upper():
                    st.warning("⚠️ Media Retrieval Error\n- Check your PEXELS_API_KEY is valid\n- Check internet connection\n- Verify API rate limits")
                elif "MEMORY" in error_msg.upper() or "CUDA" in error_msg or "MPS" in error_msg:
                    st.warning("⚠️ Memory/GPU Error\n- Try switching to gTTS engine (lighter weight)\n- Close other applications\n- Use shorter duration (30 seconds)")
                elif "ffmpeg" in error_msg.lower():
                    st.warning("⚠️ FFmpeg Error\n- Install FFmpeg: `brew install ffmpeg` on macOS\n- Or: pip install imageio-ffmpeg")
                else:
                    st.info("💡 **Try these steps:**\n1. Close and restart the server\n2. Switch TTS Engine to 'gtts'\n3. Verify API keys in .env\n4. Check terminal for detailed error logs")
                
                # Always show traceback in expander for debugging
                with st.expander("See full error details"):
                    st.code(traceback.format_exc(), language="python")
                return

        st.success("Video generation complete")

        st.subheader("Final Video")
        st.video(result.final_video_path)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Script JSON")
            script_data = _load_json(result.script_json_path)
            st.json(script_data)
            with open(result.script_json_path, "rb") as f:
                st.download_button(
                    label="Download script.json",
                    data=f,
                    file_name="script.json",
                    mime="application/json",
                )

        with col2:
            st.subheader("Assets Used")
            assets_data = _load_json(result.assets_json_path)
            st.json(assets_data)
            with open(result.assets_json_path, "rb") as f:
                st.download_button(
                    label="Download assets_used.json",
                    data=f,
                    file_name="assets_used.json",
                    mime="application/json",
                )

        with open(result.final_video_path, "rb") as f:
            st.download_button(
                label="Download final_video.mp4",
                data=f,
                file_name="final_video.mp4",
                mime="video/mp4",
            )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("💡 **Troubleshooting tips:**\n- Ensure FFmpeg is installed: `brew install ffmpeg`\n- Try switching TTS Engine to 'gtts'\n- Check that .env file has valid API keys\n- Restart the server: `streamlit run streamlit_app.py --logger.level=debug`")
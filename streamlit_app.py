import json
import os
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


def main() -> None:
    st.set_page_config(page_title="AI Educational Video Generator", layout="wide")
    st.title("AI Educational Video Generator")
    st.caption("Create a 30-60 second educational video from a topic")

    with st.sidebar:
        st.header("Inputs")
        topic = st.text_input("Topic", value="The water cycle")
        audience = st.selectbox("Target audience", options=["kids", "students", "general"], index=1)
        tone = st.selectbox("Tone", options=["formal", "engaging", "storytelling"], index=1)
        duration = st.slider("Duration (seconds)", min_value=30, max_value=60, value=45, step=1)
        tts_engine = st.selectbox("TTS Engine", options=["speecht5", "gtts"], index=0, help="SpeechT5 is recommended for better audio quality")
        output_dir = st.text_input("Output directory", value="outputs")
        bgm_path = st.text_input("Optional background music path", value="")
        generate = st.button("Generate Video", type="primary")

    if generate:
        if not topic.strip():
            st.error("Please enter a topic.")
            return

        with st.spinner("Generating video. This can take a few minutes..."):
            try:
                result = generate_video(
                    topic=topic.strip(),
                    audience=audience,
                    tone=tone,
                    duration_seconds=int(duration),
                    output_dir=output_dir.strip() or "outputs",
                    background_music_path=bgm_path.strip() or None,
                    tts_engine=tts_engine,
                )
            except Exception as exc:
                st.error(f"Generation failed: {exc}")
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
    main()
try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("💡 **Troubleshooting tips:**\n- Ensure FFmpeg is installed: `brew install ffmpeg`\n- Try switching TTS Engine to 'gtts'\n- Check that .env file has valid API keys\n- Restart the server: `streamlit run streamlit_app.py --logger.level=debug`"
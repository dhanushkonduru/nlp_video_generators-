# AI Educational Video Generator

An automated pipeline to generate high-quality educational videos from text topics using AI-powered script generation, media retrieval, speech synthesis, and video assembly.

## Features

- **AI Script Generation**: Uses Grok API to generate engaging educational scripts tailored to different audiences (kids, students, general)
- **Speech Synthesis**: Supports both SpeechT5 (high-quality neural) and gTTS (fallback) engines
- **Media Retrieval**: Automatically fetches relevant images from Pexels API
- **Caption Generation**: Adds synchronized captions to videos
- **Video Assembly**: Combines audio, visuals, and captions into a polished MP4 video
- **Dual Interfaces**: CLI for automation, Streamlit web UI for interactive use

## Prerequisites

- Python 3.10+
- FFmpeg (installed on system or via pip)
- API Keys:
  - [Grok API](https://console.x.ai/) (for script generation)
  - [Pexels API](https://www.pexels.com/api/) (for image retrieval)

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd nlp_video_generators-
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API keys
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GROK_API_KEY=your_grok_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
```

## Usage

### Web Interface (Streamlit)
```bash
streamlit run streamlit_app.py
```

Then:
1. Enter a topic (e.g., "The water cycle")
2. Select audience and tone
3. Choose duration (30-60 seconds)
4. Select TTS engine (SpeechT5 recommended)
5. Click "Generate Video"

### Command Line Interface (CLI)
```bash
python cli.py \
  --topic "The Solar System" \
  --audience students \
  --tone engaging \
  --duration 45 \
  --tts speecht5 \
  --output-dir outputs
```

**Available options:**
- `--topic`: Topic for the video (required)
- `--audience`: Target audience - `kids`, `students`, or `general` (required)
- `--tone`: Narrative tone - `formal`, `engaging`, or `storytelling` (required)
- `--duration`: Video duration in seconds, 30-60 (required)
- `--tts`: Text-to-speech engine - `speecht5` (default) or `gtts`
- `--output-dir`: Output directory for generated files (default: `outputs`)
- `--bgm`: Optional background music file path

### Example Output
```
outputs/
├── The_water_cycle_20260401_113459/
│   ├── final_video.mp4          # Generated video
│   ├── script.json              # Generated script
│   ├── assets_used.json         # Media sources
│   ├── narration.wav            # Audio file
│   └── captions/                # Caption files
└── The_Sun_20260401_120623/
    ├── final_video.mp4
    ├── script.json
    └── ...
```

## Project Structure

```
.
├── cli.py                          # Command-line interface
├── streamlit_app.py                # Web UI
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment variables
└── src/video_generator/
    ├── main.py                     # Main pipeline
    ├── config.py                   # Configuration management
    ├── content_generation.py       # Script generation with Grok API
    ├── speech_synthesis.py         # Audio generation (SpeechT5/gTTS)
    ├── media_retrieval.py          # Image fetching from Pexels
    ├── caption_generation.py       # Caption creation
    ├── video_assembly.py           # Video composition
    ├── ffmpeg_setup.py             # FFmpeg initialization
    ├── models.py                   # Data models
    └── utils.py                    # Utility functions
```

## Troubleshooting

### Streamlit Server Crashes on macOS
If the app exits with code 134 (SIGABRT):

1. **Ensure FFmpeg is installed:**
   ```bash
   brew install ffmpeg
   # or
   pip install imageio-ffmpeg
   ```

2. **Set torch environment variables (macOS):**
   ```bash
   export PYTORCH_ENABLE_MPS_FALLBACK=1
   export OMP_NUM_THREADS=1
   ```

3. **Use gTTS instead of SpeechT5:**
   - In the Streamlit UI, select "gtts" from TTS Engine dropdown
   - Or use CLI: `--tts gtts`

4. **Verify API keys are set:**
   ```bash
   source .env
   echo $GROK_API_KEY $PEXELS_API_KEY
   ```

### "Module not found" errors
```bash
pip install -r requirements.txt
# If issues persist, upgrade pip
pip install --upgrade pip
```

### Memory issues with large scripts
- Reduce video duration or use gTTS (smaller model)
- Close other applications to free up RAM

### Missing media in output
- Verify Pexels API key is valid and has sufficient quota
- Check network connectivity
- Review generated script for searchable keywords

## Configuration

### TTS Engine Comparison

| Feature | SpeechT5 | gTTS |
|---------|----------|------|
| Quality | High (neural) | Good |
| Speed | Slower | Faster |
| Dependencies | torch, transformers | Network-only |
| Memory | ~2GB | Minimal |
| Fallback | Automatic to gTTS | Automatic to SpeechT5 |

### Video Generation Timeline
- **Script generation**: 5-15 seconds
- **Speech synthesis**: 10-30 seconds (depends on engine)
- **Media retrieval**: 15-30 seconds
- **Caption generation**: 5-10 seconds
- **Video assembly**: 10-30 seconds

**Total**: ~1-2 minutes per video

## API Rate Limits

- **Grok API**: Check X AI console for limits
- **Pexels API**: 200 per hour (free tier)

## License

[Your License Here]

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues and questions:
- Check the Troubleshooting section
- Review API documentation
- Check GitHub Issues

---

Generated with ❤️ using AI technologies

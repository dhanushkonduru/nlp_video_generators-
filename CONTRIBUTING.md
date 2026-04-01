# Contributing to AI Educational Video Generator

Thank you for your interest in contributing! Here's how you can help.

## Getting Started

1. **Fork the repo** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nlp_video_generators.git
   cd nlp_video_generators-
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Set up development environment** (see [SETUP_MACOS.md](SETUP_MACOS.md) for macOS):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Development Workflow

### Running Tests/Debugging
```bash
# Test with CLI
python cli.py --topic "Test" --audience students --tone engaging --duration 30 --tts gtts

# Test with Streamlit
streamlit run streamlit_app.py
```

### Code Style
- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions and classes

### Making Changes
1. Create your feature branch
2. Make your changes
3. Test thoroughly (especially on macOS if you made changes to torch/audio)
4. Commit with clear messages:
   ```bash
   git commit -am "Add feature: clear description"
   ```

## Areas for Contribution

### High Priority
- [ ] Windows compatibility testing and fixes
- [ ] Linux compatibility improvements
- [ ] Better error recovery and fallback handling
- [ ] Performance optimizations

### Medium Priority
- [ ] Video quality improvements
- [ ] New TTS engines support
- [ ] Caption styling options
- [ ] Batch video processing

### Lower Priority
- [ ] Documentation improvements
- [ ] UI/UX enhancements
- [ ] Code refactoring
- [ ] Test coverage

## Bug Reports

Found a bug? Please create an issue with:
1. **Steps to reproduce**
2. **Expected behavior**
3. **Actual behavior**
4. **Environment** (OS, Python version, API key status)
5. **Error message** (if applicable)

**For macOS users**: If you hit the exit 134 crash, see [SETUP_MACOS.md](SETUP_MACOS.md)

## Feature Requests

Have an idea? Open an issue with:
1. **Use case**: Why is this needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Any other approaches?

## Pull Request Process

1. **Update [README.md](README.md)** with details of changes if applicable
2. **Update docstrings** for modified functions
3. **Test on your platform** (especially macOS M1/M2/M3)
4. **Create PR** with:
   - Clear title and description
   - Reference to related issues
   - Details of what you changed

## Project Structure

```
src/video_generator/
├── main.py              # Main pipeline (don't break this!)
├── config.py            # Configuration loading
├── content_generation.py # Grok API integration
├── speech_synthesis.py   # TTS (SpeechT5/gTTS)
├── media_retrieval.py    # Pexels API integration
├── caption_generation.py # Caption creation
├── video_assembly.py     # FFmpeg video composition
├── ffmpeg_setup.py       # FFmpeg initialization
├── models.py             # Data structures
└── utils.py              # Helper functions
```

## Key Files to Know

- **speech_synthesis.py**: Torch/transformers stability - if modifying, test on macOS!
- **ffmpeg_setup.py**: FFmpeg initialization - critical for video assembly
- **config.py**: API key and path management
- **video_assembly.py**: Complex FFmpeg operations - test thoroughly

## Testing Checklist

Before submitting a PR:
- [ ] Code runs without errors
- [ ] No new warnings/deprecations
- [ ] Works with both `speecht5` and `gtts` TTS engines
- [ ] Generates valid output JSON files
- [ ] Video file is playable
- [ ] Works on your OS (macOS/Linux/Windows)

## Questions?

- Check [README.md](README.md) for general info
- Check [SETUP_MACOS.md](SETUP_MACOS.md) for macOS issues
- Open a GitHub discussion

---

**Happy coding!**

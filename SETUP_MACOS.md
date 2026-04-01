# macOS Setup Guide

This guide helps resolve common issues on macOS when running the AI Educational Video Generator.

## Common Issue: Server Crashes (Exit Code 134)

Exit code 134 usually means the process received a SIGABRT signal. This commonly happens on macOS due to torch/transformers compatibility issues.

### Quick Fix (Try This First)

```bash
# 1. Install FFmpeg via Homebrew (if not already installed)
brew install ffmpeg

# 2. Create .env file from template
cp .env.example .env
# Edit .env with your API keys

# 3. Run with gTTS instead of SpeechT5
streamlit run streamlit_app.py
```

Then in the Streamlit UI:
- **TTS Engine dropdown**: Select `gtts` instead of `speecht5`
- This uses a lightweight online service instead of local torch models

### Solution 2: Fix torch for macOS

If you want to use SpeechT5:

```bash
# Set environment variables for torch stability
export PYTORCH_ENABLE_MPS_FALLBACK=1
export OMP_NUM_THREADS=1

# Restart the app
streamlit run streamlit_app.py
```

Or create a `.env` file with:
```
PYTORCH_ENABLE_MPS_FALLBACK=1
OMP_NUM_THREADS=1
GROK_API_KEY=your_key
PEXELS_API_KEY=your_key
```

### Solution 3: Use CPU instead of GPU

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
streamlit run streamlit_app.py
```

The app will automatically fall back to CPU if MPS device fails.

### Solution 4: Fresh Install (Nuclear Option)

```bash
# Remove virtual environment
rm -rf venv

# Create new environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Run
streamlit run streamlit_app.py
```

## Installation Troubleshooting

### Issue: "No module named transformers"
```bash
source venv/bin/activate
pip install transformers torch torchaudio
```

### Issue: "FFmpeg not found"
```bash
# Check if ffmpeg is installed
which ffmpeg

# Install if missing
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### Issue: "ModuleNotFoundError: No module named 'PIL'"
```bash
pip install Pillow
```

### Issue: "ImportError: No module named 'moviepy'"
```bash
pip install moviepy
```

## Apple Silicon (M1/M2/M3) Specific

For best results on Apple Silicon:

1. **Use native Python**, not x86 via Rosetta
2. **Install via Homebrew**:
   ```bash
   brew install python@3.11
   /opt/homebrew/bin/python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Set PyTorch to use native MPS**:
   ```bash
   export PYTORCH_ENABLE_MPS_FALLBACK=1
   ```

## Performance Tips

### For Video Generation Speed
- Use **gTTS** for faster audio (Recommended for macOS)
- Reduce **Duration** to 30 seconds minimum
- Close other applications to free up memory
- Use **SpeechT5** only if you need high-quality audio

### For Memory Issues
- Switch to gTTS (much lighter)
- Generate shorter videos
- Close Chrome/Safari/IDEs while running

## Debugging

### Run with Debug Logging
```bash
streamlit run streamlit_app.py --logger.level=debug
```

### Check Python Version
```bash
python --version
# Should be 3.10 or higher
```

### Check Installation
```bash
python -c "import torch; print(torch.backends.mps.is_available())"
# Should print: True (for M1/M2/M3) or False (for Intel)
```

### Check FFmpeg
```bash
which ffmpeg
ffmpeg -version
```

## Still Having Issues?

1. **Check .env file exists and has valid API keys**:
   ```bash
   cat .env
   ```

2. **Verify virtual environment is activated**:
   ```bash
   which python
   # Should show something like: /path/to/venv/bin/python
   ```

3. **Try CLI instead of Streamlit**:
   ```bash
   python cli.py \
     --topic "Test" \
     --audience students \
     --tone engaging \
     --duration 30 \
     --tts gtts
   ```

4. **Check system resources**:
   ```bash
   # Open Activity Monitor and check memory/CPU usage
   open -a "Activity Monitor"
   ```

## Getting Help

If you still can't get it working:
1. Include output from: `python --version && which python && ffmpeg -version`
2. Post the full error message from the terminal
3. Specify your Mac model (Intel/M1/M2/M3) and macOS version

---

**Recommended Setup for macOS**:
- Use **Python 3.11** from Homebrew
- Use **gTTS** engine initially
- Switch to **SpeechT5** only if needed

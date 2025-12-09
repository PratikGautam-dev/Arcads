# AI Video Ads - Audio Pipeline

Complete audio generation pipeline for AI-powered video ad creation. Converts text to high-quality speech using ElevenLabs, then refines the audio for optimal lip-sync processing.

## 🎯 What This Does

```
Text Input → ElevenLabs TTS → Raw MP3 → Audio Refinement → Refined WAV → Ready for MuseTalk
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```
ELEVENLABS_API_KEY=your_api_key_here
```

Get your API key from: https://elevenlabs.io/app/settings/api-keys

### 3. Install FFmpeg

**Windows (with winget):**
```bash
winget install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### 4. Run Test

```bash
python tests/test_tts.py
```

## 📖 Usage

### Simple Usage

```python
from src import quick_generate

# Generate audio from text
text = "Transform your fitness journey with our AI-powered app!"
result = quick_generate(text)

if result['success']:
    print(f"Raw audio: {result['raw_audio']}")
    print(f"Refined audio: {result['refined_audio']}")
    print(f"Duration: {result['metadata']['duration']}s")
```

### Advanced Usage

```python
from src import generate_refined_audio

# Custom voice and output name
result = generate_refined_audio(
    text="Your ad script here",
    voice_id="pNInz6obpgDQGcFmaJgB",  # Adam voice
    output_name="my_custom_ad"
)
```

### Available Voices

| Voice | ID | Description |
|-------|-----|-------------|
| Rachel | `21m00Tcm4TlvDq8ikWAM` | Natural female voice (default) |
| Adam | `pNInz6obpgDQGcFmaJgB` | Deep male voice |
| Antoni | `ErXwobaYiN019PkySvjV` | Well-rounded male voice |
| Elli | `MF3mGyEYCl7XYWbV9V6O` | Emotional female voice |

## 📁 Project Structure

```
ai-video-ads/
├── audio_raw/          # Raw MP3 files from ElevenLabs
├── audio_refined/      # Processed WAV files (ready for MuseTalk)
├── config/
│   └── config.yaml     # Configuration settings
├── src/
│   ├── __init__.py     # Main pipeline orchestrator
│   ├── tts_service.py  # ElevenLabs integration
│   ├── audio_refiner.py # Audio processing
│   └── utils.py        # Helper functions
├── tests/
│   └── test_tts.py     # Test suite
└── logs/               # Processing logs
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

- **Voice settings**: Stability, similarity, style
- **Noise reduction**: Strength (0-1)
- **Normalization**: Target volume (-20dB to -16dB)
- **Output format**: Sample rate, bit depth

## 🎨 Audio Processing Pipeline

1. **Text-to-Speech**: ElevenLabs generates natural speech
2. **Noise Reduction**: Removes background noise and artifacts
3. **Volume Normalization**: Adjusts to -18dB (optimal for dialog)
4. **Voice Enhancement**: Gentle compression for clarity
5. **Format Conversion**: Converts to WAV (22050Hz, 16-bit, mono)

## 📊 Output Specifications

**Refined Audio (WAV):**
- Format: WAV
- Sample Rate: 22050 Hz (MuseTalk compatible)
- Bit Depth: 16-bit
- Channels: Mono
- Volume: Normalized to -18dB

## 🧪 Testing

Run the complete test suite:

```bash
python tests/test_tts.py
```

This tests:
- Basic audio generation
- Ad script processing
- Different voices
- Error handling

## 📝 Example Scripts

### Generate Multiple Ads

```python
from src import generate_refined_audio

ad_scripts = [
    "Discover the future of fitness!",
    "Transform your workout routine today!",
    "Join thousands of satisfied users!"
]

for i, script in enumerate(ad_scripts):
    result = generate_refined_audio(
        text=script,
        output_name=f"ad_{i+1}"
    )
    print(f"Generated: {result['refined_audio']}")
```

### Batch Process with Different Voices

```python
voices = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "adam": "pNInz6obpgDQGcFmaJgB"
}

text = "Your ad script here"

for name, voice_id in voices.items():
    result = generate_refined_audio(
        text=text,
        voice_id=voice_id,
        output_name=f"ad_{name}"
    )
```

## 🔍 Troubleshooting

### "ELEVENLABS_API_KEY not found"
- Create `.env` file in project root
- Add your API key: `ELEVENLABS_API_KEY=your_key_here`

### "No module named 'distutils'"
- You're using Python 3.13+
- Install setuptools: `pip install setuptools`

### "FFmpeg not found"
- Install FFmpeg (see Quick Start section)
- Restart terminal after installation
- Verify: `ffmpeg -version`

### Audio quality issues
- Adjust noise reduction strength in `config.yaml`
- Try different target_db values (-20 to -16)
- Experiment with voice settings (stability, similarity)

## 📦 Next Steps: Video Integration

The refined WAV files are ready for MuseTalk lip-sync:

1. Upload refined audio to Google Colab
2. Run MuseTalk with your audio + reference image
3. Generate final video ad

## 🤝 Contributing

This is Phase 1 of the AI video ad platform. Next phases:
- Phase 2: MuseTalk video generation
- Phase 3: Web interface
- Phase 4: Batch processing automation

## 📄 License

MIT License

## 🆘 Support

Issues? Questions? Check:
- Logs in `logs/` directory
- ElevenLabs API docs: https://elevenlabs.io/docs
- FFmpeg troubleshooting: https://ffmpeg.org/

---

**Ready to generate amazing voice-overs for your video ads!** 🎙️✨
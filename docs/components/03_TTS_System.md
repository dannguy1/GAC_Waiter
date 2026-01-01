## TTS (Text-to-Speech) System

### Overview
The TTS system provides on-demand, multi-language voice synthesis for waiter responses using Piper TTS with automatic language detection.

### Architecture

**On-Demand Generation**:
- TTS audio is NOT generated automatically with chat responses
- Users click 🔊 button next to waiter messages to generate and play audio
- Faster chat responses since TTS is optional

**Multi-Language Support**:
- **English**: `en_US-amy-medium.onnx` (60MB)
- **Vietnamese**: `vi_VN-vais1000-medium.onnx` (60MB)
- **Spanish**: `es_ES-sharvard-medium.onnx` (73MB)

**Language Detection**:
- Uses `langdetect` library to automatically identify text language
- Selects appropriate voice model based on detected language
- Falls back to English for unsupported languages

**Text Processing**:
- **Markdown Stripping**: Removes all markdown formatting (`**bold**`, `*italic*`, `` `code` ``, `[links]()`, etc.)
- **Emoji Suppression**: Strips all unicode emojis and symbols (e.g., 👋, 🌿) to prevent literal pronunciation
- **Line Break Handling**: Replaces newlines with spaces for continuous speech
- **Whitespace Cleanup**: Normalizes multiple spaces

**Caching**:
- Cache key includes language code and original text
- Prevents regeneration for repeated messages
- Stored in `cache/tts/` directory

### API Endpoints

**POST /v1/tts**
- Request: `{"text": "message to speak"}`
- Response: `{"audio_base64": "..."}`
- Detects language, strips markdown, generates audio
- Returns base64-encoded WAV file

**POST /v1/chat**
- Does NOT generate audio automatically
- Returns only text and mentioned items
- Faster response times

### Implementation

**Backend** (`backend/tts_client.py`):
- `TTSClient` class manages multiple voice models
- `_detect_language()`: Identifies text language
- `_strip_markdown()`: Cleans text for natural speech
- `generate_audio()`: Selects model and generates audio

**Frontend** (`app.py`):
- 🔊 button next to each assistant message
- `api_tts()`: Calls TTS endpoint on demand
- Audio cached in session state (`audio_{idx}`)
- Autoplay when button clicked

### Benefits
- ⚡ Faster chat (no automatic TTS generation)
- 🌍 Multi-language support (3 languages)
- 🎯 Natural pronunciation (native voices)
- 💾 Efficient caching (language-specific)
- 🔇 User control (on-demand playback)

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered movie translation and dubbing system built with Python. The system automatically processes video files to:
1. Extract audio and perform speech recognition
2. Translate subtitles to Chinese
3. Identify different characters/voices
4. Clone voices and generate Chinese dubbing
5. Synthesize dubbed audio back into the original video

## Development Environment

- **Language**: Python 3.10+
- **Package Manager**: UV (modern Python package manager)
- **Primary UI Framework**: CustomTkinter / PySide6 for desktop GUI
- **Backend Service**: FastAPI for local API server
- **Database**: SQLite for local data storage
- **Machine Learning**: PyTorch with various AI models

## Key Dependencies

### Core Frameworks
- `customtkinter>=5.2.0` - Modern desktop GUI framework
- `pyside6>=6.5.0` - Alternative UI framework
- `fastapi>=0.100.0` - Local API server
- `uvicorn>=0.23.0` - ASGI server for FastAPI

### AI/ML Libraries
- `torch>=2.0.0` - Deep learning framework
- `transformers>=4.30.0` - Hugging Face models
- `openai>=1.0.0` - OpenAI API integration
- `ffmpeg-python>=0.2.0` - Video/audio processing

### Audio Processing
- `pydub>=0.25.1` - Audio manipulation
- `soundfile>=0.12.0` - Audio file I/O
- `pyttsx3>=2.90` - Text-to-speech

### Data & Storage
- `sqlalchemy>=2.0.0` - Database ORM
- `alembic>=1.11.0` - Database migrations
- `redis>=4.6.0` - Caching layer
- `celery>=5.3.0` - Task queue

### Development Tools
- `pytest>=7.4.0` - Testing framework
- `black>=23.0.0` - Code formatting
- `flake8>=6.0.0` - Linting
- `mypy>=1.5.0` - Type checking

## Common Commands

### Running the Application
```bash
# Run the main application
python main.py

# Install dependencies with UV
uv sync

# Run with UV
uv run python main.py
```

### Development
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Package Management
```bash
# Add new dependency
uv add <package-name>

# Remove dependency
uv remove <package-name>

# Update dependencies
uv sync --upgrade
```

## Architecture Overview

The system follows a layered architecture:

1. **Desktop App Layer** (CustomTkinter/PySide6)
   - Main UI with file drag-and-drop
   - Real-time progress display
   - Character management interface
   - Settings and configuration

2. **Local Service Layer** (FastAPI)
   - RESTful APIs for internal communication
   - WebSocket for real-time updates
   - Task queue management
   - Progress synchronization

3. **Business Logic Layer**
   - Video processing service
   - Speech recognition (SenseVoice local / Baidu cloud)
   - Translation service (DeepSeek R1 / GLM-4.5)
   - Character identification
   - Voice cloning (F5-TTS local / MiniMax cloud)

4. **Data Storage Layer**
   - SQLite for structured data
   - File system cache for intermediate results
   - Redis for session management

## Processing Pipeline

The main processing flow consists of 6 steps:
1. **File Import** - Video/audio file validation and preparation
2. **Audio Processing** - Extract audio from video, format conversion
3. **Speech Recognition** - Generate original language subtitles
4. **Translation** - Convert subtitles to Chinese
5. **Character Identification** - Identify different speakers and voice characteristics
6. **Voice Cloning & Dubbing** - Generate Chinese audio with cloned voices

## Key Features

### User Experience
- Drag-and-drop file upload
- Real-time progress tracking with step-by-step visualization
- Cache management with interrupt/resume capability
- Character management with voice preview
- Flexible error handling and recovery

### Technical Features
- Hybrid processing (local models + cloud APIs)
- Step-level caching for efficient interrupt recovery
- Multi-format support (MP4, AVI, MKV, MP3, WAV, etc.)
- GPU acceleration for local models
- Automatic quality assessment

## Configuration

### Model Selection
- **Speech Recognition**: SenseVoice (local) or Baidu Speech (cloud)
- **Translation**: DeepSeek R1 (primary) or GLM-4.5 (backup)
- **Voice Cloning**: F5-TTS (local) or MiniMax Audio (cloud)

### API Integration
The system integrates with multiple cloud services:
- Baidu Speech API
- DeepSeek R1 API
- GLM-4.5 API
- MiniMax Audio API

API keys and configuration are managed through the settings interface.

## Development Notes

- The project uses UV as the package manager instead of pip
- Main entry point is `main.py`
- The system is designed to work offline using local models
- Cloud APIs are used as fallback or for enhanced quality
- Caching is critical for performance and user experience
- The UI is built with desktop-first design principles
"""
Test configuration and fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

from movie_translate.core.config import Settings
from movie_translate.core.logger import setup_logger
from movie_translate.models.database_models import Base, get_db_manager
from movie_translate.models.repositories import get_repositories


@pytest.fixture(scope="session")
def test_dir():
    """Create a temporary directory for tests"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def test_settings(test_dir):
    """Create test settings"""
    settings = Settings()
    settings.app_dir = test_dir
    settings.config_file = test_dir / "config.json"
    settings.log_file = test_dir / "test.log"
    settings.database.url = f"sqlite:///{test_dir}/test.db"
    settings.cache.path = str(test_dir / "cache")
    settings.cache.temp_path = str(test_dir / "temp")
    
    # Create directories
    test_dir.mkdir(parents=True, exist_ok=True)
    Path(settings.cache.path).mkdir(parents=True, exist_ok=True)
    Path(settings.cache.temp_path).mkdir(parents=True, exist_ok=True)
    
    return settings


@pytest.fixture(scope="session")
def test_logger(test_settings):
    """Setup test logger"""
    return setup_logger(
        name="test_logger",
        log_file=test_settings.log_file,
        level="DEBUG"
    )


@pytest.fixture(scope="function")
def test_db(test_settings):
    """Create test database"""
    # Initialize database
    db_manager = get_db_manager()
    db_manager.engine = None
    db_manager.SessionLocal = None
    
    # Create test database
    from sqlalchemy import create_engine
    engine = create_engine(test_settings.database.url, echo=False)
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_db):
    """Create test database session"""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_repositories():
    """Get test repositories"""
    return get_repositories()


@pytest.fixture
def mock_audio_file(test_dir):
    """Create a mock audio file"""
    audio_file = test_dir / "test_audio.wav"
    audio_file.write_text("mock audio content")
    return str(audio_file)


@pytest.fixture
def mock_video_file(test_dir):
    """Create a mock video file"""
    video_file = test_dir / "test_video.mp4"
    video_file.write_text("mock video content")
    return str(video_file)


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "name": "Test Project",
        "description": "Test project for unit tests",
        "video_file_path": "/path/to/test/video.mp4",
        "video_format": "mp4",
        "video_duration": 120.5,
        "video_size": 1024000,
        "video_resolution": "1920x1080",
        "source_language": "zh",
        "target_language": "en",
        "voice_cloning_service": "f5-tts",
        "translation_service": "google",
        "output_format": "mp4",
        "output_quality": "high"
    }


@pytest.fixture
def sample_character_data():
    """Sample character data for testing"""
    return {
        "name": "Test Character",
        "description": "Test character for unit tests",
        "language": "zh",
        "gender": "male",
        "age_group": "adult"
    }


@pytest.fixture
def sample_audio_segment_data():
    """Sample audio segment data for testing"""
    return {
        "start_time": 0.0,
        "end_time": 5.0,
        "file_path": "/path/to/audio/segment.wav",
        "file_format": "wav",
        "file_size": 512000,
        "sample_rate": 16000,
        "channels": 1,
        "original_text": "Hello, world!",
        "confidence": 0.95,
        "language_detected": "en"
    }


@pytest.fixture
def sample_translation_data():
    """Sample translation data for testing"""
    return {
        "source_language": "en",
        "target_language": "zh",
        "source_text": "Hello, world!",
        "translated_text": "你好，世界！",
        "confidence": 0.92,
        "quality_score": 0.88,
        "translation_service": "google",
        "processing_time": 0.5
    }


@pytest.fixture
def mock_api_client():
    """Mock API client"""
    mock_client = Mock()
    mock_client.health_check.return_value = {"status": "healthy"}
    mock_client.create_project.return_value = {"id": "test_project_id"}
    return mock_client


@pytest.fixture
def mock_progress_manager():
    """Mock progress manager"""
    mock_manager = Mock()
    mock_manager.update_progress.return_value = None
    mock_manager.complete_task.return_value = None
    return mock_manager


@pytest.fixture
def mock_cache_manager():
    """Mock cache manager"""
    mock_manager = Mock()
    mock_manager.get.return_value = None
    mock_manager.set.return_value = True
    mock_manager.delete.return_value = True
    return mock_manager
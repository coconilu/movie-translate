"""
Unit tests for configuration module
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from movie_translate.core.config import (
    Settings, AudioSettings, CacheSettings, ProcessingSettings,
    ServiceSettings, APISettings, APIKeys, DatabaseSettings, UISettings,
    VoiceCloneService, SpeechRecognitionService, TranslationService
)


class TestAudioSettings:
    """Test AudioSettings class"""
    
    def test_default_values(self):
        """Test default audio settings"""
        settings = AudioSettings()
        assert settings.sample_rate == 16000
        assert settings.channels == 1
        assert settings.format == "wav"
        assert settings.quality == "high"
        assert settings.noise_reduction is True
        assert settings.normalize is True


class TestCacheSettings:
    """Test CacheSettings class"""
    
    def test_default_values(self):
        """Test default cache settings"""
        settings = CacheSettings()
        assert settings.enabled is True
        assert settings.max_size_gb == 10.0
        assert settings.cleanup_days == 7
        assert settings.path == "resources/cache"
        assert settings.temp_path == "resources/temp"


class TestProcessingSettings:
    """Test ProcessingSettings class"""
    
    def test_default_values(self):
        """Test default processing settings"""
        settings = ProcessingSettings()
        assert settings.max_retries == 3
        assert settings.timeout_seconds == 300
        assert settings.batch_size == 100
        assert settings.parallel_workers == 2
        assert settings.enable_interrupt is True
        assert settings.auto_save is True


class TestServiceSettings:
    """Test ServiceSettings class"""
    
    def test_default_values(self):
        """Test default service settings"""
        settings = ServiceSettings()
        assert settings.speech_recognition == SpeechRecognitionService.SENSE_VOICE
        assert settings.translation == TranslationService.DEEPSEEK
        assert settings.voice_clone == VoiceCloneService.F5_TTS
        assert settings.fallback_to_local is True
        assert settings.cost_budget_monthly == 50.0


class TestAPISettings:
    """Test APISettings class"""
    
    def test_default_values(self):
        """Test default API settings"""
        settings = APISettings()
        assert settings.host == "localhost"
        assert settings.port == 8000
        assert settings.debug is False
        assert settings.cors_origins == ["*"]
        assert settings.max_file_size == 100 * 1024 * 1024
        assert settings.timeout == 300
        assert settings.enable_docs is True


class TestAPIKeys:
    """Test APIKeys class"""
    
    def test_default_values(self):
        """Test default API keys"""
        keys = APIKeys()
        assert keys.baidu_speech_app_id is None
        assert keys.baidu_speech_api_key is None
        assert keys.baidu_speech_secret_key is None
        assert keys.deepseek_api_key is None
        assert keys.glm_api_key is None
        assert keys.google_translate_api_key is None
        assert keys.minimax_api_key is None
        assert keys.minimax_group_id is None


class TestDatabaseSettings:
    """Test DatabaseSettings class"""
    
    def test_default_values(self):
        """Test default database settings"""
        settings = DatabaseSettings()
        assert settings.url == "sqlite:///movie_translate.db"
        assert settings.echo is False
        assert settings.pool_size == 10
        assert settings.max_overflow == 20
        assert settings.pool_timeout == 30
        assert settings.pool_recycle == 3600


class TestUISettings:
    """Test UISettings class"""
    
    def test_default_values(self):
        """Test default UI settings"""
        settings = UISettings()
        assert settings.theme == "system"
        assert settings.language == "zh-CN"
        assert settings.window_width == 1200
        assert settings.window_height == 800
        assert settings.auto_check_updates is True
        assert settings.show_advanced_options is False


class TestSettings:
    """Test Settings class"""
    
    def test_default_values(self):
        """Test default settings"""
        settings = Settings()
        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.__version__ == "1.0.0"
        
        # Check that all components are initialized
        assert isinstance(settings.audio, AudioSettings)
        assert isinstance(settings.cache, CacheSettings)
        assert isinstance(settings.processing, ProcessingSettings)
        assert isinstance(settings.service, ServiceSettings)
        assert isinstance(settings.api, APISettings)
        assert isinstance(settings.api_keys, APIKeys)
        assert isinstance(settings.database, DatabaseSettings)
        assert isinstance(settings.ui, UISettings)
    
    def test_post_init_creates_directories(self, test_dir):
        """Test that __post_init__ creates necessary directories"""
        settings = Settings()
        settings.app_dir = test_dir
        settings.config_file = test_dir / "config.json"
        settings.log_file = test_dir / "app.log"
        settings.cache.path = str(test_dir / "cache")
        settings.cache.temp_path = str(test_dir / "temp")
        
        settings.__post_init__()
        
        # Check that directories were created
        assert test_dir.exists()
        assert (test_dir / "cache").exists()
        assert (test_dir / "temp").exists()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_save_settings(self, mock_mkdir, mock_exists, mock_file, test_settings):
        """Test saving settings to file"""
        mock_exists.return_value = True
        
        test_settings.save()
        
        # Check that file was opened for writing
        mock_file.assert_called_once_with(test_settings.config_file, 'w', encoding='utf-8')
        
        # Check that json.dump was called
        handle = mock_file()
        assert handle.write.called
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    @patch('json.load')
    def test_load_settings(self, mock_json_load, mock_exists, mock_file, test_settings):
        """Test loading settings from file"""
        # Mock file exists and has content
        mock_exists.return_value = True
        
        mock_config_data = {
            "audio": {
                "sample_rate": 44100,
                "channels": 2
            },
            "debug": True,
            "log_level": "DEBUG"
        }
        mock_json_load.return_value = mock_config_data
        
        test_settings.load()
        
        # Check that settings were updated
        assert test_settings.audio.sample_rate == 44100
        assert test_settings.audio.channels == 2
        assert test_settings.debug is True
        assert test_settings.log_level == "DEBUG"
    
    def test_get_cache_path(self, test_settings):
        """Test getting cache path"""
        cache_path = test_settings.get_cache_path()
        assert isinstance(cache_path, Path)
        assert str(cache_path) == test_settings.cache.path
    
    def test_get_temp_path(self, test_settings):
        """Test getting temp path"""
        temp_path = test_settings.get_temp_path()
        assert isinstance(temp_path, Path)
        assert str(temp_path) == test_settings.cache.temp_path
    
    def test_get_log_path(self, test_settings):
        """Test getting log path"""
        log_path = test_settings.get_log_path()
        assert log_path == test_settings.log_file
    
    def test_get_api_key(self, test_settings):
        """Test getting API key"""
        test_settings.api_keys.test_key = "test_value"
        assert test_settings.get_api_key("test_key") == "test_value"
        assert test_settings.get_api_key("nonexistent_key") is None
    
    def test_get_database_url_with_env_var(self, test_settings):
        """Test getting database URL with environment variable"""
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost/test'}):
            db_url = test_settings.get_database_url()
            assert db_url == 'postgresql://test:test@localhost/test'
    
    def test_get_database_url_without_env_var(self, test_settings):
        """Test getting database URL without environment variable"""
        with patch.dict(os.environ, {}, clear=True):
            db_url = test_settings.get_database_url()
            assert db_url == test_settings.database.url
    
    def test_get_system_info(self, test_settings):
        """Test getting system information"""
        system_info = test_settings.get_system_info()
        
        assert isinstance(system_info, dict)
        assert "platform" in system_info
        assert "platform_version" in system_info
        assert "architecture" in system_info
        assert "processor" in system_info
        assert "python_version" in system_info
        assert "app_dir" in system_info
        assert "config_file" in system_info
        assert "log_file" in system_info
        assert "database_url" in system_info
    
    def test_reset_to_defaults(self, test_settings):
        """Test resetting settings to defaults"""
        # Modify some settings
        test_settings.debug = True
        test_settings.audio.sample_rate = 44100
        test_settings.cache.enabled = False
        
        # Reset to defaults
        test_settings.reset_to_defaults()
        
        # Check that settings were reset
        assert test_settings.debug is False
        assert test_settings.audio.sample_rate == 16000
        assert test_settings.cache.enabled is True


if __name__ == "__main__":
    pytest.main([__file__])
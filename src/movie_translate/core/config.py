"""
Configuration management module for Movie Translate
"""

import os
import json
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class ServiceType(Enum):
    """Service type enumeration"""
    LOCAL = "local"
    CLOUD = "cloud"


class VoiceCloneService(Enum):
    """Voice clone service enumeration"""
    F5_TTS = "f5_tts"
    MINIMAX = "minimax"


class SpeechRecognitionService(Enum):
    """Speech recognition service enumeration"""
    SENSE_VOICE = "sense_voice"
    BAIDU = "baidu"


class TranslationService(Enum):
    """Translation service enumeration"""
    DEEPSEEK = "deepseek"
    GLM = "glm"
    GOOGLE = "google"


@dataclass
class AudioSettings:
    """Audio processing settings"""
    sample_rate: int = 16000
    channels: int = 1
    format: str = "wav"
    quality: str = "high"
    noise_reduction: bool = True
    normalize: bool = True
    chunk_size: int = 1024


@dataclass
class CacheSettings:
    """Cache management settings"""
    enabled: bool = True
    max_size_gb: float = 10.0
    cleanup_days: int = 7
    path: str = "resources/cache"
    temp_path: str = "resources/temp"


@dataclass
class ProcessingSettings:
    """Processing pipeline settings"""
    max_retries: int = 3
    timeout_seconds: int = 300
    batch_size: int = 100
    parallel_workers: int = 2
    enable_interrupt: bool = True
    auto_save: bool = True


@dataclass
class ServiceSettings:
    """Service configuration settings"""
    speech_recognition: SpeechRecognitionService = SpeechRecognitionService.SENSE_VOICE
    translation: TranslationService = TranslationService.DEEPSEEK
    voice_clone: VoiceCloneService = VoiceCloneService.F5_TTS
    fallback_to_local: bool = True
    cost_budget_monthly: float = 50.0


@dataclass
class SpeechRecognitionSettings:
    """Speech recognition specific settings"""
    primary_service: SpeechRecognitionService = SpeechRecognitionService.SENSE_VOICE
    default_language: str = "zh"
    batch_size: int = 100
    enable_diarization: bool = True
    min_speech_duration: float = 0.5
    max_silence_gap: float = 2.0


@dataclass
class TranslationSettings:
    """Translation specific settings"""
    primary_service: TranslationService = TranslationService.DEEPSEEK
    default_source_language: str = "zh"
    default_target_language: str = "en"
    batch_size: int = 100
    deepseek_model: str = "deepseek-chat"
    glm_model: str = "glm-4"
    enable_cache: bool = True
    max_retries: int = 3


@dataclass
class VoiceCloningSettings:
    """Voice cloning specific settings"""
    primary_service: VoiceCloneService = VoiceCloneService.F5_TTS
    minimax_model_id: str = "speech-01"
    minimax_voice_id: str = "female-tianmei-jingpin"
    batch_size: int = 10
    enable_cache: bool = True
    max_retries: int = 3
    quality_preset: str = "high"


@dataclass
class VideoSettings:
    """Video processing settings"""
    target_resolution: str = "1920x1080"
    target_fps: int = 30
    target_bitrate: str = "5000k"
    target_codec: str = "libx264"
    target_format: str = "mp4"
    quality_preset: str = "high"
    enable_gpu_acceleration: bool = True


@dataclass
class APISettings:
    """API server settings"""
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    timeout: int = 300
    enable_docs: bool = True


@dataclass
class APIKeys:
    """API keys configuration"""
    baidu_speech_app_id: Optional[str] = None
    baidu_speech_api_key: Optional[str] = None
    baidu_speech_secret_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    glm_api_key: Optional[str] = None
    google_translate_api_key: Optional[str] = None
    minimax_api_key: Optional[str] = None
    minimax_group_id: Optional[str] = None


@dataclass
class DatabaseSettings:
    """Database configuration settings"""
    url: str = "sqlite:///movie_translate.db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class UISettings:
    """User interface settings"""
    theme: str = "system"  # light, dark, system
    language: str = "zh-CN"
    window_width: int = 1200
    window_height: int = 800
    auto_check_updates: bool = True
    show_advanced_options: bool = False


@dataclass
class Settings:
    """Main settings class"""
    audio: AudioSettings = field(default_factory=AudioSettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    processing: ProcessingSettings = field(default_factory=ProcessingSettings)
    service: ServiceSettings = field(default_factory=ServiceSettings)
    speech: SpeechRecognitionSettings = field(default_factory=SpeechRecognitionSettings)
    translation: TranslationSettings = field(default_factory=TranslationSettings)
    voice_cloning: VoiceCloningSettings = field(default_factory=VoiceCloningSettings)
    video: VideoSettings = field(default_factory=VideoSettings)
    api: APISettings = field(default_factory=APISettings)
    api_keys: APIKeys = field(default_factory=APIKeys)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    ui: UISettings = field(default_factory=UISettings)
    
    # Paths
    app_dir: Path = field(default_factory=lambda: Path.home() / ".movie-translate")
    config_file: Path = field(default_factory=lambda: Path.home() / ".movie-translate" / "config.json")
    log_file: Path = field(default_factory=lambda: Path.home() / ".movie-translate" / "app.log")
    
    # Development
    debug: bool = False
    log_level: str = "INFO"
    
    # Version
    __version__: str = "1.0.0"
    
    def __post_init__(self):
        """Initialize paths after creation"""
        self.app_dir = Path.home() / ".movie-translate"
        self.config_file = self.app_dir / "config.json"
        self.log_file = self.app_dir / "app.log"
        
        # Ensure directories exist
        self.app_dir.mkdir(parents=True, exist_ok=True)
        Path(self.cache.path).mkdir(parents=True, exist_ok=True)
        Path(self.cache.temp_path).mkdir(parents=True, exist_ok=True)
    
    def save(self) -> None:
        """Save settings to file"""
        config_data = {
            "audio": {
                "sample_rate": self.audio.sample_rate,
                "channels": self.audio.channels,
                "format": self.audio.format,
                "quality": self.audio.quality,
                "noise_reduction": self.audio.noise_reduction,
                "normalize": self.audio.normalize
            },
            "cache": {
                "enabled": self.cache.enabled,
                "max_size_gb": self.cache.max_size_gb,
                "cleanup_days": self.cache.cleanup_days,
                "path": self.cache.path,
                "temp_path": self.cache.temp_path
            },
            "processing": {
                "max_retries": self.processing.max_retries,
                "timeout_seconds": self.processing.timeout_seconds,
                "batch_size": self.processing.batch_size,
                "parallel_workers": self.processing.parallel_workers,
                "enable_interrupt": self.processing.enable_interrupt,
                "auto_save": self.processing.auto_save
            },
            "service": {
                "speech_recognition": self.service.speech_recognition.value,
                "translation": self.service.translation.value,
                "voice_clone": self.service.voice_clone.value,
                "fallback_to_local": self.service.fallback_to_local,
                "cost_budget_monthly": self.service.cost_budget_monthly
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "debug": self.api.debug,
                "cors_origins": self.api.cors_origins,
                "max_file_size": self.api.max_file_size,
                "timeout": self.api.timeout,
                "enable_docs": self.api.enable_docs
            },
            "api_keys": {
                "baidu_speech_app_id": self.api_keys.baidu_speech_app_id,
                "baidu_speech_api_key": self.api_keys.baidu_speech_api_key,
                "baidu_speech_secret_key": self.api_keys.baidu_speech_secret_key,
                "deepseek_api_key": self.api_keys.deepseek_api_key,
                "glm_api_key": self.api_keys.glm_api_key,
                "google_translate_api_key": self.api_keys.google_translate_api_key,
                "minimax_api_key": self.api_keys.minimax_api_key,
                "minimax_group_id": self.api_keys.minimax_group_id
            },
            "database": {
                "url": self.database.url,
                "echo": self.database.echo,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "pool_timeout": self.database.pool_timeout,
                "pool_recycle": self.database.pool_recycle
            },
            "ui": {
                "theme": self.ui.theme,
                "language": self.ui.language,
                "window_width": self.ui.window_width,
                "window_height": self.ui.window_height,
                "auto_check_updates": self.ui.auto_check_updates,
                "show_advanced_options": self.ui.show_advanced_options
            },
            "debug": self.debug,
            "log_level": self.log_level
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def load(self) -> None:
        """Load settings from file"""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Load audio settings
            if "audio" in config_data:
                audio_data = config_data["audio"]
                self.audio.sample_rate = audio_data.get("sample_rate", self.audio.sample_rate)
                self.audio.channels = audio_data.get("channels", self.audio.channels)
                self.audio.format = audio_data.get("format", self.audio.format)
                self.audio.quality = audio_data.get("quality", self.audio.quality)
                self.audio.noise_reduction = audio_data.get("noise_reduction", self.audio.noise_reduction)
                self.audio.normalize = audio_data.get("normalize", self.audio.normalize)
            
            # Load cache settings
            if "cache" in config_data:
                cache_data = config_data["cache"]
                self.cache.enabled = cache_data.get("enabled", self.cache.enabled)
                self.cache.max_size_gb = cache_data.get("max_size_gb", self.cache.max_size_gb)
                self.cache.cleanup_days = cache_data.get("cleanup_days", self.cache.cleanup_days)
                self.cache.path = cache_data.get("path", self.cache.path)
                self.cache.temp_path = cache_data.get("temp_path", self.cache.temp_path)
            
            # Load processing settings
            if "processing" in config_data:
                processing_data = config_data["processing"]
                self.processing.max_retries = processing_data.get("max_retries", self.processing.max_retries)
                self.processing.timeout_seconds = processing_data.get("timeout_seconds", self.processing.timeout_seconds)
                self.processing.batch_size = processing_data.get("batch_size", self.processing.batch_size)
                self.processing.parallel_workers = processing_data.get("parallel_workers", self.processing.parallel_workers)
                self.processing.enable_interrupt = processing_data.get("enable_interrupt", self.processing.enable_interrupt)
                self.processing.auto_save = processing_data.get("auto_save", self.processing.auto_save)
            
            # Load service settings
            if "service" in config_data:
                service_data = config_data["service"]
                self.service.speech_recognition = SpeechRecognitionService(service_data.get("speech_recognition", self.service.speech_recognition.value))
                self.service.translation = TranslationService(service_data.get("translation", self.service.translation.value))
                self.service.voice_clone = VoiceCloneService(service_data.get("voice_clone", self.service.voice_clone.value))
                self.service.fallback_to_local = service_data.get("fallback_to_local", self.service.fallback_to_local)
                self.service.cost_budget_monthly = service_data.get("cost_budget_monthly", self.service.cost_budget_monthly)
            
            # Load API settings
            if "api" in config_data:
                api_data = config_data["api"]
                self.api.host = api_data.get("host", self.api.host)
                self.api.port = api_data.get("port", self.api.port)
                self.api.debug = api_data.get("debug", self.api.debug)
                self.api.cors_origins = api_data.get("cors_origins", self.api.cors_origins)
                self.api.max_file_size = api_data.get("max_file_size", self.api.max_file_size)
                self.api.timeout = api_data.get("timeout", self.api.timeout)
                self.api.enable_docs = api_data.get("enable_docs", self.api.enable_docs)
            
            # Load API keys
            if "api_keys" in config_data:
                api_keys_data = config_data["api_keys"]
                self.api_keys.baidu_speech_app_id = api_keys_data.get("baidu_speech_app_id")
                self.api_keys.baidu_speech_api_key = api_keys_data.get("baidu_speech_api_key")
                self.api_keys.baidu_speech_secret_key = api_keys_data.get("baidu_speech_secret_key")
                self.api_keys.deepseek_api_key = api_keys_data.get("deepseek_api_key")
                self.api_keys.glm_api_key = api_keys_data.get("glm_api_key")
                self.api_keys.google_translate_api_key = api_keys_data.get("google_translate_api_key")
                self.api_keys.minimax_api_key = api_keys_data.get("minimax_api_key")
                self.api_keys.minimax_group_id = api_keys_data.get("minimax_group_id")
            
            # Load database settings
            if "database" in config_data:
                database_data = config_data["database"]
                self.database.url = database_data.get("url", self.database.url)
                self.database.echo = database_data.get("echo", self.database.echo)
                self.database.pool_size = database_data.get("pool_size", self.database.pool_size)
                self.database.max_overflow = database_data.get("max_overflow", self.database.max_overflow)
                self.database.pool_timeout = database_data.get("pool_timeout", self.database.pool_timeout)
                self.database.pool_recycle = database_data.get("pool_recycle", self.database.pool_recycle)
            
            # Load UI settings
            if "ui" in config_data:
                ui_data = config_data["ui"]
                self.ui.theme = ui_data.get("theme", self.ui.theme)
                self.ui.language = ui_data.get("language", self.ui.language)
                self.ui.window_width = ui_data.get("window_width", self.ui.window_width)
                self.ui.window_height = ui_data.get("window_height", self.ui.window_height)
                self.ui.auto_check_updates = ui_data.get("auto_check_updates", self.ui.auto_check_updates)
                self.ui.show_advanced_options = ui_data.get("show_advanced_options", self.ui.show_advanced_options)
            
            # Load development settings
            self.debug = config_data.get("debug", self.debug)
            self.log_level = config_data.get("log_level", self.log_level)
            
        except Exception as e:
            print(f"Failed to load settings: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset settings to default values"""
        self.__init__()
        self.save()
    
    def get_cache_path(self) -> Path:
        """Get cache directory path"""
        return Path(self.cache.path)
    
    def get_temp_path(self) -> Path:
        """Get temporary directory path"""
        return Path(self.cache.temp_path)
    
    def get_log_path(self) -> Path:
        """Get log file path"""
        return self.log_file
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "app_dir": str(self.app_dir),
            "config_file": str(self.config_file),
            "log_file": str(self.log_file)
        }
    
    def get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key by name"""
        return getattr(self.api_keys, key_name, None)
    
    def get_database_url(self) -> str:
        """Get database URL with environment variable support"""
        # Check environment variable first
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            return db_url
        
        # Use configured URL
        return self.database.url
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "app_dir": str(self.app_dir),
            "config_file": str(self.config_file),
            "log_file": str(self.log_file),
            "database_url": self.get_database_url()
        }


# Global settings instance
settings = Settings()

# Initialize settings
settings.load()
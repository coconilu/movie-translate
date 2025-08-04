"""
Movie Translate - AI-powered movie translation and dubbing system
"""

__version__ = "0.1.0"
__author__ = "Movie Translate Team"
__description__ = "AI-powered movie translation and dubbing tool"

from .core.config import settings
from .core.logger import logger
from .core.cache_manager import CacheManager

__all__ = [
    "settings",
    "logger", 
    "CacheManager"
]
"""
Logging system module for Movie Translate
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from .config import settings


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class MovieTranslateLogger:
    """Main logger class for Movie Translate"""
    
    def __init__(self):
        self.logger = logging.getLogger("movie_translate")
        self.logger.setLevel(getattr(logging, settings.log_level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()
        self._setup_error_handler()
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _setup_console_handler(self):
        """Setup console handler with colored output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Colored formatter for console
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup file handler with rotation"""
        # Ensure log directory exists
        settings.get_log_path().parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler (10MB per file, 5 backups)
        file_handler = RotatingFileHandler(
            settings.get_log_path(),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Detailed formatter for file
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_error_handler(self):
        """Setup separate error handler"""
        error_log_path = settings.get_log_path().parent / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s\n'
            'Exception: %(exc_info)s\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, **kwargs)
    
    def log_processing_step(self, step_name: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Log processing step with structured data"""
        message = f"Processing Step: {step_name} - Status: {status}"
        if details:
            message += f" - Details: {details}"
        self.info(message)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        message = f"Performance: {operation} took {duration:.2f}s"
        if kwargs:
            message += f" - {kwargs}"
        self.info(message)
    
    def log_api_call(self, service: str, endpoint: str, status: str, duration: float, **kwargs):
        """Log API call information"""
        message = f"API Call: {service} - {endpoint} - Status: {status} - Duration: {duration:.2f}s"
        if kwargs:
            message += f" - {kwargs}"
        self.info(message)
    
    def log_file_operation(self, operation: str, file_path: str, size: Optional[int] = None, **kwargs):
        """Log file operations"""
        message = f"File Operation: {operation} - {file_path}"
        if size:
            message += f" - Size: {size} bytes"
        if kwargs:
            message += f" - {kwargs}"
        self.info(message)
    
    def log_cache_operation(self, operation: str, cache_key: str, size: Optional[int] = None, **kwargs):
        """Log cache operations"""
        message = f"Cache Operation: {operation} - {cache_key}"
        if size:
            message += f" - Size: {size} bytes"
        if kwargs:
            message += f" - {kwargs}"
        self.info(message)
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """Log error with context information"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        self.error(f"Error occurred: {error_info}")
    
    def set_level(self, level: str):
        """Set logging level"""
        numeric_level = getattr(logging, level.upper(), None)
        if isinstance(numeric_level, int):
            self.logger.setLevel(numeric_level)
            settings.log_level = level.upper()
    
    def get_log_files(self) -> list:
        """Get list of log files"""
        log_dir = settings.get_log_path().parent
        return list(log_dir.glob("*.log"))
    
    def clear_logs(self):
        """Clear all log files"""
        log_files = self.get_log_files()
        for log_file in log_files:
            try:
                log_file.unlink()
            except Exception as e:
                self.error(f"Failed to delete log file {log_file}: {e}")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        log_files = self.get_log_files()
        total_size = sum(f.stat().st_size for f in log_files if f.exists())
        
        return {
            "log_files": len(log_files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "log_directory": str(settings.get_log_path().parent),
            "log_level": settings.log_level
        }


# Global logger instance
logger = MovieTranslateLogger()
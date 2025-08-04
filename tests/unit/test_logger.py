"""
Unit tests for logger module
"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from movie_translate.core.logger import setup_logger, get_logger, ColoredFormatter


class TestColoredFormatter:
    """Test ColoredFormatter class"""
    
    def test_format_with_color_codes(self):
        """Test formatting with color codes"""
        formatter = ColoredFormatter()
        
        # Create a mock log record
        record = Mock()
        record.levelname = "ERROR"
        record.getMessage.return_value = "Test message"
        
        # Format the record
        formatted = formatter.format(record)
        
        # Check that color codes are included
        assert "\033[" in formatted
        assert "Test message" in formatted
    
    def test_format_without_color_codes(self):
        """Test formatting without color codes"""
        formatter = ColoredFormatter(use_colors=False)
        
        # Create a mock log record
        record = Mock()
        record.levelname = "ERROR"
        record.getMessage.return_value = "Test message"
        
        # Format the record
        formatted = formatter.format(record)
        
        # Check that no color codes are included
        assert "\033[" not in formatted
        assert "Test message" in formatted


class TestLoggerSetup:
    """Test logger setup functionality"""
    
    def test_setup_logger_with_file(self, test_settings):
        """Test setting up logger with file output"""
        logger = setup_logger(
            name="test_logger",
            log_file=test_settings.log_file,
            level="DEBUG"
        )
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG
        
        # Check handlers
        assert len(logger.handlers) == 2  # Console and file handlers
        
        # Check that log file exists
        assert test_settings.log_file.exists()
    
    def test_setup_logger_without_file(self):
        """Test setting up logger without file output"""
        logger = setup_logger(
            name="test_logger",
            level="INFO"
        )
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        
        # Check handlers (only console)
        assert len(logger.handlers) == 1
    
    def test_setup_logger_different_levels(self, test_settings):
        """Test setting up logger with different levels"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            logger = setup_logger(
                name=f"test_logger_{level}",
                log_file=test_settings.log_file,
                level=level
            )
            
            expected_level = getattr(logging, level)
            assert logger.level == expected_level
    
    def test_setup_logger_with_custom_format(self, test_settings):
        """Test setting up logger with custom format"""
        custom_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logger = setup_logger(
            name="test_logger",
            log_file=test_settings.log_file,
            level="INFO",
            format_string=custom_format
        )
        
        # Check that format was applied to handlers
        for handler in logger.handlers:
            if isinstance(handler.formatter, ColoredFormatter):
                # For console handler, check base format
                assert custom_format in handler.formatter._fmt
            else:
                # For file handler
                assert handler.formatter._fmt == custom_format
    
    def test_logger_output_to_file(self, test_settings):
        """Test that logger writes to file"""
        logger = setup_logger(
            name="test_logger",
            log_file=test_settings.log_file,
            level="INFO"
        )
        
        # Log a message
        test_message = "Test log message"
        logger.info(test_message)
        
        # Force flush handlers
        for handler in logger.handlers:
            handler.flush()
        
        # Check that message was written to file
        if test_settings.log_file.exists():
            content = test_settings.log_file.read_text()
            assert test_message in content
    
    def test_logger_different_log_levels(self, test_settings):
        """Test logger with different log levels"""
        logger = setup_logger(
            name="test_logger",
            log_file=test_settings.log_file,
            level="WARNING"
        )
        
        # Log messages at different levels
        logger.debug("Debug message")  # Should not appear
        logger.info("Info message")    # Should not appear
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")  # Should appear
        
        # Force flush handlers
        for handler in logger.handlers:
            handler.flush()
        
        # Check file content
        if test_settings.log_file.exists():
            content = test_settings.log_file.read_text()
            assert "Debug message" not in content
            assert "Info message" not in content
            assert "Warning message" in content
            assert "Error message" in content


class TestGetLogger:
    """Test get_logger functionality"""
    
    def test_get_logger_existing(self):
        """Test getting existing logger"""
        # Create a logger first
        original_logger = setup_logger(name="test_existing_logger")
        
        # Get the same logger
        retrieved_logger = get_logger("test_existing_logger")
        
        assert retrieved_logger is original_logger
    
    def test_get_logger_nonexistent(self):
        """Test getting non-existent logger"""
        logger = get_logger("nonexistent_logger")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "nonexistent_logger"
    
    def test_get_logger_default_level(self):
        """Test getting logger with default level"""
        logger = get_logger("test_default_logger")
        
        # Should use default level from module
        assert logger.level == logging.INFO
    
    @patch('movie_translate.core.logger.setup_logger')
    def test_get_logger_calls_setup(self, mock_setup):
        """Test that get_logger calls setup_logger for new loggers"""
        mock_setup.return_value = Mock()
        
        get_logger("new_test_logger")
        
        mock_setup.assert_called_once_with("new_test_logger")


class TestLoggerIntegration:
    """Test logger integration scenarios"""
    
    def test_multiple_loggers_independence(self, test_settings):
        """Test that multiple loggers work independently"""
        # Create two loggers with different levels
        logger1 = setup_logger(
            name="logger1",
            log_file=test_settings.log_file,
            level="DEBUG"
        )
        logger2 = setup_logger(
            name="logger2",
            log_file=test_settings.log_file,
            level="ERROR"
        )
        
        # Log different messages
        logger1.debug("Debug from logger1")
        logger1.info("Info from logger1")
        logger2.debug("Debug from logger2")  # Should not appear
        logger2.error("Error from logger2")
        
        # Force flush handlers
        for handler in logger1.handlers:
            handler.flush()
        for handler in logger2.handlers:
            handler.flush()
        
        # Check file content
        if test_settings.log_file.exists():
            content = test_settings.log_file.read_text()
            assert "Debug from logger1" in content
            assert "Info from logger1" in content
            assert "Debug from logger2" not in content
            assert "Error from logger2" in content
    
    def test_logger_exception_handling(self, test_settings):
        """Test logger exception handling"""
        logger = setup_logger(
            name="test_exception_logger",
            log_file=test_settings.log_file,
            level="INFO"
        )
        
        # Log an exception
        try:
            raise ValueError("Test exception")
        except Exception as e:
            logger.exception("Exception occurred")
        
        # Force flush handlers
        for handler in logger.handlers:
            handler.flush()
        
        # Check that exception was logged
        if test_settings.log_file.exists():
            content = test_settings.log_file.read_text()
            assert "Exception occurred" in content
            assert "ValueError: Test exception" in content
            assert "Traceback" in content
    
    def test_logger_performance(self, test_settings):
        """Test logger performance with many messages"""
        logger = setup_logger(
            name="test_performance_logger",
            log_file=test_settings.log_file,
            level="INFO"
        )
        
        # Log many messages
        import time
        start_time = time.time()
        
        for i in range(1000):
            logger.info(f"Performance test message {i}")
        
        end_time = time.time()
        
        # Force flush handlers
        for handler in logger.handlers:
            handler.flush()
        
        # Check that it didn't take too long (should be < 1 second for 1000 messages)
        assert end_time - start_time < 1.0
        
        # Check that messages were written
        if test_settings.log_file.exists():
            content = test_settings.log_file.read_text()
            assert "Performance test message 0" in content
            assert "Performance test message 999" in content


if __name__ == "__main__":
    pytest.main([__file__])
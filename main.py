"""
Main application entry point for Movie Translate
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from movie_translate.core import settings, logger, progress_manager, error_handler, ErrorSeverity
from movie_translate.utils.file_utils import FileUtils
from movie_translate.utils.audio_utils import AudioUtils


def main():
    """Main application entry point"""
    try:
        # Print system information
        system_info = settings.get_system_info()
        logger.info(f"Starting Movie Translate v{settings.__version__}")
        logger.info(f"System: {system_info['platform']} {system_info['platform_version']}")
        logger.info(f"Python: {system_info['python_version']}")
        logger.info(f"App directory: {system_info['app_dir']}")
        
        # Check dependencies
        logger.info("Checking dependencies...")
        dependencies_ok = check_dependencies()
        
        if not dependencies_ok:
            logger.error("Dependency check failed. Please install required dependencies.")
            return 1
        
        # Initialize directories
        logger.info("Initializing directories...")
        initialize_directories()
        
        # Start the application
        logger.info("Application initialized successfully")
        
        # TODO: Start GUI application
        print("Movie Translate application initialized successfully!")
        print("GUI application will be implemented in the next phase.")
        
        return 0
        
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"operation": "main_application_start"},
            severity=ErrorSeverity.CRITICAL
        )
        return 1


def check_dependencies() -> bool:
    """Check if all required dependencies are available"""
    required_modules = [
        'customtkinter',
        'numpy', 
        'pandas',
        'requests',
        'torch',
        'transformers',
        'fastapi',
        'uvicorn',
        'sqlalchemy'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Missing required modules: {missing_modules}")
        return False
    
    logger.info("All required dependencies are available")
    return True


def initialize_directories():
    """Initialize required directories"""
    directories = [
        settings.get_cache_path(),
        settings.get_temp_path(),
        settings.get_log_path().parent
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {directory}")


def test_system():
    """Test system functionality"""
    logger.info("Running system tests...")
    
    # Test file operations
    test_file = settings.get_temp_path() / "test.txt"
    try:
        test_file.write_text("test content")
        content = test_file.read_text()
        test_file.unlink()
        logger.info("File operations test passed")
    except Exception as e:
        logger.error(f"File operations test failed: {e}")
    
    # Test cache operations
    try:
        from movie_translate.core.cache_manager import cache_manager
        cache_manager.put("test_key", "test_value")
        value = cache_manager.get("test_key")
        cache_manager.remove("test_key")
        logger.info("Cache operations test passed")
    except Exception as e:
        logger.error(f"Cache operations test failed: {e}")
    
    # Test progress tracking
    try:
        project = progress_manager.create_project("test_project", "Test Project", "/path/to/test")
        logger.info("Progress tracking test passed")
    except Exception as e:
        logger.error(f"Progress tracking test failed: {e}")
    
    logger.info("System tests completed")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

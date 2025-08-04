#!/usr/bin/env python3
"""
Simple test script to verify the Movie Translate project structure
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_project_structure():
    """Test that all core modules exist"""
    print("Testing project structure...")
    
    # Check core modules
    core_modules = [
        "movie_translate/core/config.py",
        "movie_translate/core/logger.py",
        "movie_translate/core/cache_manager.py",
        "movie_translate/core/error_handler.py",
        "movie_translate/models/database_models.py",
        "movie_translate/models/schemas.py",
        "movie_translate/models/repositories.py",
        "movie_translate/services/audio_processing.py",
        "movie_translate/services/speech_recognition.py",
        "movie_translate/services/translation.py",
        "movie_translate/services/character_identification.py",
        "movie_translate/services/voice_cloning.py",
        "movie_translate/services/video_synthesis.py",
        "movie_translate/ui/main_app.py",
        "movie_translate/ui/step_navigator.py",
        "movie_translate/ui/file_import.py",
        "movie_translate/ui/character_manager.py",
        "movie_translate/ui/settings_panel.py",
        "movie_translate/ui/progress_display.py",
        "movie_translate/ui/recovery_dialog.py"
    ]
    
    missing_modules = []
    for module in core_modules:
        module_path = Path(__file__).parent / "src" / module
        if not module_path.exists():
            missing_modules.append(module)
    
    if missing_modules:
        print(f"Missing modules: {missing_modules}")
        return False
    else:
        print("All core modules found")
        return True

def test_imports():
    """Test that core modules can be imported"""
    print("\nTesting imports...")
    
    try:
        from movie_translate.core.config import Settings
        from movie_translate.core.logger import MovieTranslateLogger
        from movie_translate.core.cache_manager import CacheManager
        from movie_translate.models.database_models import get_db_manager
        from movie_translate.services.audio_processing import AudioProcessor
        from movie_translate.services.translation import TranslationService
        print("Core imports successful")
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        # Test settings
        from movie_translate.core.config import settings
        print("Settings initialized")
        
        # Test logger
        from movie_translate.core.logger import logger
        logger.info("Test message")
        print("Logger working")
        
        # Test cache manager
        cache_manager = CacheManager()
        cache_manager.set("test_key", "test_value")
        value = cache_manager.get("test_key")
        assert value == "test_value"
        print("Cache manager working")
        
        return True
    except Exception as e:
        print(f"Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Movie Translate Project Verification")
    print("=" * 50)
    
    tests = [
        test_project_structure,
        test_imports,
        test_basic_functionality
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("All tests passed! Project is ready.")
        return 0
    else:
        print("Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
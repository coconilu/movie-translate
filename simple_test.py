#!/usr/bin/env python3
"""
Simple test to verify the Movie Translate project works
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_basic_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    
    try:
        import movie_translate
        print("Main package imported")
        
        from movie_translate.core.config import Settings
        print("Config imported")
        
        from movie_translate.core.logger import MovieTranslateLogger
        print("Logger imported")
        
        from movie_translate.core.cache_manager import CacheManager
        print("Cache manager imported")
        
        from movie_translate.models.database_models import get_db_manager
        print("Database models imported")
        
        from movie_translate.services.audio_processing import AudioProcessor
        print("Audio processor imported")
        
        from movie_translate.services.translation import TranslationService
        print("Translation service imported")
        
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        # Test settings
        from movie_translate.core.config import Settings
        settings = Settings()
        print("Settings working")
        
        # Test logger
        from movie_translate.core.logger import MovieTranslateLogger
        logger = MovieTranslateLogger()
        logger.logger.info("Test message")
        print("Logger working")
        
        # Test cache manager
        from movie_translate.core.cache_manager import CacheManager
        cache_manager = CacheManager()
        cache_manager.put("test_key", "test_value")
        value = cache_manager.get("test_key")
        assert value == "test_value"
        print("Cache manager working")
        
        # Test database manager
        from movie_translate.models.database_models import get_db_manager
        db_manager = get_db_manager()
        print("Database manager working")
        
        return True
    except Exception as e:
        print(f"Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Movie Translate Project Verification")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
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
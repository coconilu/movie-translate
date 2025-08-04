#!/usr/bin/env python3
"""
Simple verification script for Movie Translate project
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_basic_structure():
    """Test basic project structure"""
    print("Testing basic project structure...")
    
    required_files = [
        "src/movie_translate/core/config.py",
        "src/movie_translate/core/logger.py",
        "src/movie_translate/core/cache_manager.py",
        "src/movie_translate/ui/main_app.py",
        "src/movie_translate/services/audio_processing.py",
        "src/movie_translate/services/translation.py",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    else:
        print("All required files found")
        return True

def test_config():
    """Test configuration system"""
    print("\nTesting configuration system...")
    
    try:
        from movie_translate.core.config import Settings
        settings = Settings()
        print("✓ Settings class works")
        
        # Test some basic settings
        print(f"✓ Audio sample rate: {settings.audio.sample_rate}")
        print(f"✓ Cache enabled: {settings.cache.enabled}")
        print(f"✓ Debug mode: {settings.debug}")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_logger():
    """Test logging system"""
    print("\nTesting logging system...")
    
    try:
        from movie_translate.core.logger import MovieTranslateLogger
        logger = MovieTranslateLogger()
        logger.info("Test message from verification")
        print("✓ Logger works")
        
        return True
    except Exception as e:
        print(f"✗ Logger test failed: {e}")
        return False

def test_cache():
    """Test cache system"""
    print("\nTesting cache system...")
    
    try:
        from movie_translate.core.cache_manager import CacheManager
        cache = CacheManager()
        cache.put("test_key", "test_value")
        value = cache.get("test_key")
        
        if value == "test_value":
            print("✓ Cache manager works")
            return True
        else:
            print("✗ Cache value mismatch")
            return False
            
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Movie Translate Project - Simple Verification")
    print("=" * 50)
    
    tests = [
        test_basic_structure,
        test_config,
        test_logger,
        test_cache
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
        print("✅ All basic tests passed! Project structure is working.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
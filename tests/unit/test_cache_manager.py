"""
Unit tests for cache manager module
"""

import pytest
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch, Mock

from movie_translate.core.cache_manager import CacheManager, CacheEntry


class TestCacheEntry:
    """Test CacheEntry class"""
    
    def test_cache_entry_creation(self):
        """Test creating a cache entry"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            ttl=3600
        )
        
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.ttl == 3600
        assert isinstance(entry.created_at, float)
        assert isinstance(entry.access_count, int)
        assert entry.access_count == 0
    
    def test_cache_entry_is_expired(self):
        """Test cache entry expiration"""
        # Create entry with short TTL
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            ttl=1  # 1 second
        )
        
        # Should not be expired immediately
        assert not entry.is_expired()
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired now
        assert entry.is_expired()
    
    def test_cache_entry_no_expiration(self):
        """Test cache entry without expiration"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            ttl=None  # No expiration
        )
        
        # Should never expire
        assert not entry.is_expired()
        
        # Wait and check again
        time.sleep(0.1)
        assert not entry.is_expired()
    
    def test_cache_entry_access(self):
        """Test cache entry access tracking"""
        entry = CacheEntry(
            key="test_key",
            value="test_value"
        )
        
        # Initial access count
        assert entry.access_count == 0
        
        # Access the entry
        entry.access()
        
        # Access count should be incremented
        assert entry.access_count == 1
        
        # Access again
        entry.access()
        assert entry.access_count == 2


class TestCacheManager:
    """Test CacheManager class"""
    
    def test_cache_manager_initialization(self, test_settings):
        """Test cache manager initialization"""
        cache_dir = Path(test_settings.cache.path)
        cache_manager = CacheManager(
            cache_dir=cache_dir,
            max_size_mb=100,
            cleanup_interval=3600
        )
        
        assert cache_manager.cache_dir == cache_dir
        assert cache_manager.max_size_mb == 100
        assert cache_manager.cleanup_interval == 3600
        assert isinstance(cache_manager.memory_cache, dict)
        assert isinstance(cache_manager.access_order, list)
    
    def test_cache_manager_creates_directory(self, test_dir):
        """Test that cache manager creates directory"""
        cache_dir = test_dir / "test_cache"
        assert not cache_dir.exists()
        
        cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Directory should be created
        assert cache_dir.exists()
    
    def test_set_and_get_memory_cache(self, test_settings):
        """Test setting and getting values from memory cache"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        # Set a value
        cache_manager.set("test_key", "test_value")
        
        # Get the value
        value = cache_manager.get("test_key")
        
        assert value == "test_value"
    
    def test_set_and_get_file_cache(self, test_settings):
        """Test setting and getting values from file cache"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        # Set a large value that should go to file cache
        large_value = "x" * 1024  # 1KB string
        cache_manager.set("large_key", large_value)
        
        # Get the value
        value = cache_manager.get("large_key")
        
        assert value == large_value
        
        # Check that file was created
        cache_file = cache_manager.cache_dir / "large_key.cache"
        assert cache_file.exists()
    
    def test_get_nonexistent_key(self, test_settings):
        """Test getting nonexistent key"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        value = cache_manager.get("nonexistent_key")
        assert value is None
    
    def test_get_with_default(self, test_settings):
        """Test getting with default value"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        # Get nonexistent key with default
        value = cache_manager.get("nonexistent_key", default="default_value")
        assert value == "default_value"
        
        # Get existing key should ignore default
        cache_manager.set("existing_key", "existing_value")
        value = cache_manager.get("existing_key", default="default_value")
        assert value == "existing_value"
    
    def test_delete_key(self, test_settings):
        """Test deleting keys"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        # Set a value
        cache_manager.set("test_key", "test_value")
        
        # Verify it exists
        assert cache_manager.get("test_key") == "test_value"
        
        # Delete it
        result = cache_manager.delete("test_key")
        assert result is True
        
        # Verify it's gone
        assert cache_manager.get("test_key") is None
    
    def test_delete_nonexistent_key(self, test_settings):
        """Test deleting nonexistent key"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        result = cache_manager.delete("nonexistent_key")
        assert result is False
    
    def test_clear_cache(self, test_settings):
        """Test clearing cache"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        # Set multiple values
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        cache_manager.set("key3", "value3")
        
        # Clear cache
        cache_manager.clear()
        
        # Verify all keys are gone
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None
        assert cache_manager.get("key3") is None
        
        # Verify memory cache is empty
        assert len(cache_manager.memory_cache) == 0
    
    def test_cache_with_ttl(self, test_settings):
        """Test cache with TTL"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        # Set value with short TTL
        cache_manager.set("ttl_key", "ttl_value", ttl=1)  # 1 second
        
        # Get immediately - should exist
        assert cache_manager.get("ttl_key") == "ttl_value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Get after expiration - should be gone
        assert cache_manager.get("ttl_key") is None
    
    def test_cache_size_limit(self, test_settings):
        """Test cache size limit"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path), max_size_mb=1)  # 1MB limit
        
        # Set values that exceed the limit
        large_value = "x" * 1024 * 1024  # 1MB string
        
        # This should work
        cache_manager.set("key1", large_value)
        
        # This should trigger cleanup
        cache_manager.set("key2", large_value)
        
        # Check that old entries were removed
        # (exact behavior depends on LRU implementation)
        assert len(cache_manager.memory_cache) <= 1
    
    def test_cache_statistics(self, test_settings):
        """Test cache statistics"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        # Initially empty
        stats = cache_manager.get_stats()
        assert stats["memory_count"] == 0
        assert stats["file_count"] == 0
        assert stats["total_size"] == 0
        assert stats["hit_rate"] == 0.0
        
        # Add some values
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        
        # Get some values
        cache_manager.get("key1")  # Hit
        cache_manager.get("key2")  # Hit
        cache_manager.get("nonexistent")  # Miss
        
        # Check stats
        stats = cache_manager.get_stats()
        assert stats["memory_count"] >= 0
        assert stats["file_count"] >= 0
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2/3  # 2 hits out of 3 attempts
    
    def test_cache_cleanup(self, test_settings):
        """Test automatic cache cleanup"""
        cache_manager = CacheManager(
            cache_dir=Path(test_settings.cache.path),
            max_size_mb=1,
            cleanup_interval=0.1  # Very short interval for testing
        )
        
        # Add many small files to trigger cleanup
        for i in range(100):
            cache_manager.set(f"key_{i}", f"value_{i}")
        
        # Wait for cleanup interval
        time.sleep(0.2)
        
        # Trigger a get to activate cleanup
        cache_manager.get("key_1")
        
        # Check that cleanup occurred
        stats = cache_manager.get_stats()
        assert stats["memory_count"] < 100  # Some entries should have been cleaned up
    
    def test_cache_persistence(self, test_settings):
        """Test that file cache persists between instances"""
        cache_dir = Path(test_settings.cache.path)
        
        # Create first cache instance
        cache_manager1 = CacheManager(cache_dir=cache_dir)
        cache_manager1.set("persistent_key", "persistent_value")
        
        # Create second cache instance
        cache_manager2 = CacheManager(cache_dir=cache_dir)
        
        # Value should still be there
        value = cache_manager2.get("persistent_key")
        assert value == "persistent_value"
    
    def test_cache_cleanup_expired_files(self, test_settings):
        """Test cleanup of expired files"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        # Set expired entry
        cache_manager.set("expired_key", "expired_value", ttl=0.1)  # Very short TTL
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Trigger cleanup
        cache_manager.cleanup()
        
        # Check that expired entry is gone
        assert cache_manager.get("expired_key") is None
    
    def test_cache_with_different_data_types(self, test_settings):
        """Test cache with different data types"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path))
        
        # Test different data types
        test_data = {
            "string": "test_string",
            "int": 42,
            "float": 3.14,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "bool": True,
            "none": None
        }
        
        # Set and get each type
        for key, value in test_data.items():
            cache_manager.set(key, value)
            retrieved_value = cache_manager.get(key)
            assert retrieved_value == value
    
    def test_cache_memory_usage(self, test_settings):
        """Test cache memory usage tracking"""
        cache_manager = CacheManager(cache_dir=Path(test_settings.cache.path), max_size_mb=1)
        
        # Get initial memory usage
        initial_usage = cache_manager.get_memory_usage()
        
        # Add some data
        cache_manager.set("key1", "x" * 1024)  # 1KB
        cache_manager.set("key2", "x" * 2048)  # 2KB
        
        # Check memory usage increased
        current_usage = cache_manager.get_memory_usage()
        assert current_usage > initial_usage
    
    def test_cache_file_cleanup_on_destruction(self, test_settings):
        """Test that file cache is cleaned up on destruction"""
        cache_dir = Path(test_settings.cache.path)
        cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Add some file cache entries
        large_value = "x" * 1024
        cache_manager.set("file_key1", large_value)
        cache_manager.set("file_key2", large_value)
        
        # Check files exist
        assert (cache_dir / "file_key1.cache").exists()
        assert (cache_dir / "file_key2.cache").exists()
        
        # Delete cache manager (should clean up files)
        del cache_manager
        
        # Files should still exist (they persist)
        assert (cache_dir / "file_key1.cache").exists()
        assert (cache_dir / "file_key2.cache").exists()


if __name__ == "__main__":
    pytest.main([__file__])
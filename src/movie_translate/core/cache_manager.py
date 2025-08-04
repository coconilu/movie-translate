"""
Cache management module for Movie Translate
"""

import os
import json
import pickle
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List, Union, Callable
from dataclasses import dataclass, asdict
import threading
import time

from .config import settings
from .logger import logger


@dataclass
class CacheEntry:
    """Cache entry metadata"""
    key: str
    file_path: str
    created_at: datetime
    accessed_at: datetime
    expires_at: Optional[datetime]
    size: int
    metadata: Dict[str, Any]
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "key": self.key,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "size": self.size,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary"""
        return cls(
            key=data["key"],
            file_path=data["file_path"],
            created_at=datetime.fromisoformat(data["created_at"]),
            accessed_at=datetime.fromisoformat(data["accessed_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None,
            size=data["size"],
            metadata=data["metadata"]
        )


class CacheManager:
    """Cache management system for Movie Translate"""
    
    def __init__(self):
        self.cache_dir = settings.get_cache_path()
        self.temp_dir = settings.get_temp_path()
        self.index_file = self.cache_dir / "cache_index.json"
        self.lock = threading.Lock()
        self.index: Dict[str, CacheEntry] = {}
        
        # Ensure directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Load cache index
        self._load_index()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _load_index(self):
        """Load cache index from file"""
        if not self.index_file.exists():
            return
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.index = {}
            for key, entry_data in data.items():
                self.index[key] = CacheEntry.from_dict(entry_data)
            
            logger.info(f"Loaded {len(self.index)} cache entries from index")
        except Exception as e:
            logger.error(f"Failed to load cache index: {e}")
            self.index = {}
    
    def _save_index(self):
        """Save cache index to file"""
        try:
            with self.lock:
                data = {key: entry.to_dict() for key, entry in self.index.items()}
                with open(self.index_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, (str, bytes)):
            content = data
        elif isinstance(data, dict):
            content = json.dumps(data, sort_keys=True)
        else:
            content = str(data)
        
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        hash_obj = hashlib.md5(content)
        return f"{prefix}_{hash_obj.hexdigest()}"
    
    def _get_file_path(self, key: str, extension: str = "") -> Path:
        """Get file path for cache key"""
        if extension:
            return self.cache_dir / f"{key}{extension}"
        return self.cache_dir / key
    
    def _get_temp_path(self, prefix: str = "temp") -> Path:
        """Get temporary file path"""
        timestamp = int(time.time() * 1000)
        return self.temp_dir / f"{prefix}_{timestamp}"
    
    def put(self, key: str, data: Any, ttl: Optional[int] = None, 
            metadata: Optional[Dict[str, Any]] = None, 
            extension: str = "") -> str:
        """Store data in cache"""
        with self.lock:
            file_path = self._get_file_path(key, extension)
            
            try:
                # Save data
                if isinstance(data, (str, bytes)):
                    if isinstance(data, str):
                        data = data.encode('utf-8')
                    with open(file_path, 'wb') as f:
                        f.write(data)
                elif isinstance(data, dict):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    with open(file_path, 'wb') as f:
                        pickle.dump(data, f)
                
                # Get file size
                size = file_path.stat().st_size
                
                # Create cache entry
                now = datetime.now()
                expires_at = None
                if ttl:
                    expires_at = now + timedelta(seconds=ttl)
                
                entry = CacheEntry(
                    key=key,
                    file_path=str(file_path),
                    created_at=now,
                    accessed_at=now,
                    expires_at=expires_at,
                    size=size,
                    metadata=metadata or {}
                )
                
                self.index[key] = entry
                self._save_index()
                
                logger.log_cache_operation("put", key, size, metadata=metadata)
                return str(file_path)
                
            except Exception as e:
                logger.error(f"Failed to cache data for key {key}: {e}")
                # Clean up on failure
                if file_path.exists():
                    file_path.unlink()
                raise
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get data from cache"""
        with self.lock:
            if key not in self.index:
                return default
            
            entry = self.index[key]
            
            # Check if expired
            if entry.is_expired():
                self.remove(key)
                return default
            
            # Check if file exists
            file_path = Path(entry.file_path)
            if not file_path.exists():
                self.remove(key)
                return default
            
            try:
                # Update access time
                entry.accessed_at = datetime.now()
                self._save_index()
                
                # Load data
                if file_path.suffix == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                elif file_path.suffix in ['.txt', '.srt', '.ass']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    with open(file_path, 'rb') as f:
                        return pickle.load(f)
                        
            except Exception as e:
                logger.error(f"Failed to load cached data for key {key}: {e}")
                self.remove(key)
                return default
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        with self.lock:
            if key not in self.index:
                return False
            
            entry = self.index[key]
            if entry.is_expired():
                self.remove(key)
                return False
            
            return Path(entry.file_path).exists()
    
    def remove(self, key: str) -> bool:
        """Remove entry from cache"""
        with self.lock:
            if key not in self.index:
                return False
            
            entry = self.index[key]
            file_path = Path(entry.file_path)
            
            try:
                if file_path.exists():
                    file_path.unlink()
                
                del self.index[key]
                self._save_index()
                
                logger.log_cache_operation("remove", key)
                return True
                
            except Exception as e:
                logger.error(f"Failed to remove cache entry {key}: {e}")
                return False
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            for key in list(self.index.keys()):
                self.remove(key)
            
            # Clear index file
            if self.index_file.exists():
                self.index_file.unlink()
            
            logger.info("Cache cleared")
    
    def cleanup(self):
        """Clean up expired and old entries"""
        with self.lock:
            removed_count = 0
            
            # Remove expired entries
            for key in list(self.index.keys()):
                entry = self.index[key]
                if entry.is_expired():
                    if self.remove(key):
                        removed_count += 1
            
            # Remove old entries if cache is too large
            cache_size = self.get_total_size()
            max_size = settings.cache.max_size_gb * 1024 * 1024 * 1024
            
            if cache_size > max_size:
                # Sort by access time (oldest first)
                entries = sorted(self.index.values(), key=lambda x: x.accessed_at)
                
                for entry in entries:
                    if cache_size <= max_size * 0.8:  # Clean up to 80% of max size
                        break
                    
                    if self.remove(entry.key):
                        cache_size -= entry.size
                        removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cache cleanup completed: {removed_count} entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_size = sum(entry.size for entry in self.index.values())
            total_entries = len(self.index)
            
            expired_count = sum(1 for entry in self.index.values() if entry.is_expired())
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_count,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "cache_directory": str(self.cache_dir),
                "temp_directory": str(self.temp_dir),
                "max_size_gb": settings.cache.max_size_gb,
                "cleanup_days": settings.cache.cleanup_days
            }
    
    def get_entries(self) -> List[CacheEntry]:
        """Get all cache entries"""
        with self.lock:
            return list(self.index.values())
    
    def get_entry(self, key: str) -> Optional[CacheEntry]:
        """Get specific cache entry"""
        with self.lock:
            return self.index.get(key)
    
    def get_total_size(self) -> int:
        """Get total cache size in bytes"""
        with self.lock:
            return sum(entry.size for entry in self.index.values())
    
    def create_temp_file(self, prefix: str = "temp", extension: str = "") -> Path:
        """Create temporary file"""
        temp_path = self._get_temp_path(prefix)
        if extension:
            temp_path = temp_path.with_suffix(extension)
        return temp_path
    
    def move_to_cache(self, temp_path: Path, key: str, ttl: Optional[int] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Move temporary file to cache"""
        if not temp_path.exists():
            raise FileNotFoundError(f"Temporary file not found: {temp_path}")
        
        cache_path = self._get_file_path(key, temp_path.suffix)
        
        try:
            shutil.move(str(temp_path), str(cache_path))
            
            # Create cache entry
            size = cache_path.stat().st_size
            now = datetime.now()
            expires_at = None
            if ttl:
                expires_at = now + timedelta(seconds=ttl)
            
            entry = CacheEntry(
                key=key,
                file_path=str(cache_path),
                created_at=now,
                accessed_at=now,
                expires_at=expires_at,
                size=size,
                metadata=metadata or {}
            )
            
            with self.lock:
                self.index[key] = entry
                self._save_index()
            
            logger.log_cache_operation("move_to_cache", key, size)
            return str(cache_path)
            
        except Exception as e:
            logger.error(f"Failed to move temp file to cache: {e}")
            raise
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while True:
                time.sleep(3600)  # Check every hour
                try:
                    self.cleanup()
                except Exception as e:
                    logger.error(f"Cache cleanup failed: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self._save_index()
        except:
            pass


# Global cache manager instance
cache_manager = CacheManager()
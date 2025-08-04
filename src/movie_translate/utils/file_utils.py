"""
File utilities for Movie Translate
"""

import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import uuid

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity


class FileUtils:
    """File utility functions"""
    
    # Supported video formats
    VIDEO_FORMATS = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'
    }
    
    # Supported audio formats
    AUDIO_FORMATS = {
        '.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma', '.opus'
    }
    
    # Supported subtitle formats
    SUBTITLE_FORMATS = {
        '.srt', '.ass', '.ssa', '.vtt', '.sub'
    }
    
    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = file_path.stat()
            
            info = {
                'path': str(file_path),
                'name': file_path.name,
                'stem': file_path.stem,
                'suffix': file_path.suffix.lower(),
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir(),
                'mime_type': mimetypes.guess_type(str(file_path))[0]
            }
            
            # Determine file type
            info['file_type'] = FileUtils.get_file_type(file_path)
            
            # Get duration for media files
            if info['file_type'] in ['video', 'audio']:
                info['duration'] = FileUtils.get_media_duration(file_path)
            
            return info
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"file_path": str(file_path), "operation": "get_file_info"},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            raise
    
    @staticmethod
    def get_file_type(file_path: Union[str, Path]) -> str:
        """Determine file type based on extension"""
        suffix = Path(file_path).suffix.lower()
        
        if suffix in FileUtils.VIDEO_FORMATS:
            return 'video'
        elif suffix in FileUtils.AUDIO_FORMATS:
            return 'audio'
        elif suffix in FileUtils.SUBTITLE_FORMATS:
            return 'subtitle'
        else:
            return 'unknown'
    
    @staticmethod
    def is_supported_format(file_path: Union[str, Path]) -> bool:
        """Check if file format is supported"""
        file_type = FileUtils.get_file_type(file_path)
        return file_type in ['video', 'audio', 'subtitle']
    
    @staticmethod
    def validate_file(file_path: Union[str, Path], min_size: int = 1024, 
                     max_size: int = 10 * 1024 * 1024 * 1024) -> bool:
        """Validate file for processing"""
        try:
            file_path = Path(file_path)
            
            # Check if file exists
            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            # Check if it's a file
            if not file_path.is_file():
                logger.error(f"Path is not a file: {file_path}")
                return False
            
            # Check file size
            size = file_path.stat().st_size
            if size < min_size:
                logger.error(f"File too small: {size} bytes < {min_size} bytes")
                return False
            
            if size > max_size:
                logger.error(f"File too large: {size} bytes > {max_size} bytes")
                return False
            
            # Check file format
            if not FileUtils.is_supported_format(file_path):
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                logger.error(f"File is not readable: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"file_path": str(file_path), "operation": "validate_file"},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    @staticmethod
    def get_media_duration(file_path: Union[str, Path]) -> Optional[float]:
        """Get media file duration in seconds"""
        try:
            import cv2
            
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if fps > 0:
                duration = frame_count / fps
                cap.release()
                return duration
            
            cap.release()
            return None
            
        except ImportError:
            logger.warning("OpenCV not available, cannot get media duration")
            return None
        except Exception as e:
            logger.warning(f"Could not get media duration for {file_path}: {e}")
            return None
    
    @staticmethod
    def generate_unique_filename(original_path: Union[str, Path], 
                                prefix: str = "", suffix: str = "",
                                target_dir: Optional[Union[str, Path]] = None) -> Path:
        """Generate unique filename to avoid conflicts"""
        original_path = Path(original_path)
        
        if target_dir:
            target_dir = Path(target_dir)
        else:
            target_dir = original_path.parent
        
        # Create base filename
        base_name = f"{prefix}{original_path.stem}{suffix}"
        extension = original_path.suffix
        
        # Try simple name first
        new_path = target_dir / f"{base_name}{extension}"
        if not new_path.exists():
            return new_path
        
        # Add timestamp if conflict
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = target_dir / f"{base_name}_{timestamp}{extension}"
        if not new_path.exists():
            return new_path
        
        # Add UUID if still conflict
        unique_id = str(uuid.uuid4())[:8]
        new_path = target_dir / f"{base_name}_{timestamp}_{unique_id}{extension}"
        return new_path
    
    @staticmethod
    def copy_file_with_progress(source: Union[str, Path], 
                              destination: Union[str, Path],
                              progress_callback: Optional[callable] = None) -> Path:
        """Copy file with progress callback"""
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        # Ensure destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        file_size = source.stat().st_size
        copied_size = 0
        
        logger.log_file_operation("copy_start", str(source), file_size)
        
        try:
            with open(source, 'rb') as src_file, open(destination, 'wb') as dst_file:
                while True:
                    chunk = src_file.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    
                    dst_file.write(chunk)
                    copied_size += len(chunk)
                    
                    if progress_callback:
                        progress = copied_size / file_size
                        progress_callback(progress, copied_size, file_size)
            
            logger.log_file_operation("copy_complete", str(destination), file_size)
            return destination
            
        except Exception as e:
            # Clean up partial copy
            if destination.exists():
                destination.unlink()
            
            error_handler.handle_error(
                error=e,
                context={"source": str(source), "destination": str(destination)},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    @staticmethod
    def move_file_safely(source: Union[str, Path], 
                       destination: Union[str, Path]) -> Path:
        """Move file safely with conflict resolution"""
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        # Generate unique destination if needed
        if destination.exists():
            destination = FileUtils.generate_unique_filename(destination)
        
        # Ensure destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.move(str(source), str(destination))
            logger.log_file_operation("move", str(source), source.stat().st_size, 
                                    destination=str(destination))
            return destination
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"source": str(source), "destination": str(destination)},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    @staticmethod
    def delete_file_safely(file_path: Union[str, Path]) -> bool:
        """Delete file safely"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return True
        
        try:
            size = file_path.stat().st_size
            file_path.unlink()
            logger.log_file_operation("delete", str(file_path), size)
            return True
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"file_path": str(file_path)},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    @staticmethod
    def clean_directory(directory: Union[str, Path], 
                       extensions: Optional[List[str]] = None,
                       older_than_days: Optional[int] = None) -> int:
        """Clean directory by file criteria"""
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return 0
        
        deleted_count = 0
        cutoff_time = None
        
        if older_than_days:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(days=older_than_days)
        
        try:
            for file_path in directory.iterdir():
                if not file_path.is_file():
                    continue
                
                # Check extension
                if extensions and file_path.suffix.lower() not in extensions:
                    continue
                
                # Check age
                if cutoff_time and datetime.fromtimestamp(file_path.stat().st_mtime) > cutoff_time:
                    continue
                
                # Delete file
                if FileUtils.delete_file_safely(file_path):
                    deleted_count += 1
            
            logger.info(f"Cleaned directory {directory}: {deleted_count} files deleted")
            return deleted_count
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"directory": str(directory), "extensions": extensions, "older_than_days": older_than_days},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            return 0
    
    @staticmethod
    def calculate_file_hash(file_path: Union[str, Path], 
                           algorithm: str = 'md5') -> Optional[str]:
        """Calculate file hash"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"file_path": str(file_path), "algorithm": algorithm},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.LOW
            )
            return None
    
    @staticmethod
    def get_directory_size(directory: Union[str, Path]) -> int:
        """Get total size of directory"""
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return 0
        
        try:
            total_size = 0
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"directory": str(directory)},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.LOW
            )
            return 0
    
    @staticmethod
    def ensure_directory(directory: Union[str, Path]) -> Path:
        """Ensure directory exists"""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory
    
    @staticmethod
    def find_files_by_pattern(directory: Union[str, Path], 
                             pattern: str) -> List[Path]:
        """Find files by pattern"""
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return []
        
        try:
            return list(directory.glob(pattern))
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"directory": str(directory), "pattern": pattern},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.LOW
            )
            return []
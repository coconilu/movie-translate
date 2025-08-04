"""
Error handling module for Movie Translate
"""

import traceback
import sys
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
import json
import threading
from pathlib import Path

from .config import settings
from .logger import logger
from .progress_manager import progress_manager


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    API = "api"
    PROCESSING = "processing"
    MEMORY = "memory"
    HARDWARE = "hardware"
    CONFIGURATION = "configuration"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    """Recovery actions"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"
    NOTIFY_USER = "notify_user"
    LOG_ONLY = "log_only"


@dataclass
class ErrorInfo:
    """Error information structure"""
    error_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    recovery_action: RecoveryAction = RecoveryAction.LOG_ONLY
    retry_count: int = 0
    max_retries: int = 3
    is_handled: bool = False
    project_id: Optional[str] = None
    step_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "error_type": self.error_type,
            "error_message": self.error_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context,
            "stack_trace": self.stack_trace,
            "recovery_action": self.recovery_action.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "is_handled": self.is_handled,
            "project_id": self.project_id,
            "step_id": self.step_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorInfo':
        """Create from dictionary"""
        return cls(
            error_id=data["error_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            error_type=data["error_type"],
            error_message=data["error_message"],
            severity=ErrorSeverity(data["severity"]),
            category=ErrorCategory(data["category"]),
            context=data["context"],
            stack_trace=data["stack_trace"],
            recovery_action=RecoveryAction(data["recovery_action"]),
            retry_count=data["retry_count"],
            max_retries=data["max_retries"],
            is_handled=data["is_handled"],
            project_id=data["project_id"],
            step_id=data["step_id"]
        )


class ErrorHandler:
    """Error handling system for Movie Translate"""
    
    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self.error_callbacks: List[Callable] = []
        self.recovery_strategies: Dict[str, Callable] = {}
        self.lock = threading.Lock()
        
        # Register default recovery strategies
        self._register_default_strategies()
        
        # Load error history
        self._load_error_history()
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    category: ErrorCategory = ErrorCategory.UNKNOWN,
                    recovery_action: RecoveryAction = RecoveryAction.LOG_ONLY,
                    project_id: Optional[str] = None,
                    step_id: Optional[str] = None) -> ErrorInfo:
        """Handle an error"""
        
        # Create error info
        error_info = ErrorInfo(
            error_id=self._generate_error_id(),
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            category=category,
            context=context or {},
            stack_trace=traceback.format_exc(),
            recovery_action=recovery_action,
            project_id=project_id,
            step_id=step_id
        )
        
        # Add to history
        with self.lock:
            self.error_history.append(error_info)
            self._save_error_history()
        
        # Log error
        self._log_error(error_info)
        
        # Notify callbacks
        self._notify_error_callbacks(error_info)
        
        # Attempt recovery
        if not error_info.is_handled:
            self._attempt_recovery(error_info)
        
        return error_info
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register a recovery strategy for specific error types"""
        self.recovery_strategies[error_type] = strategy
        logger.info(f"Registered recovery strategy for error type: {error_type}")
    
    def register_error_callback(self, callback: Callable):
        """Register error callback"""
        self.error_callbacks.append(callback)
    
    def get_error_history(self, limit: Optional[int] = None, 
                         severity: Optional[ErrorSeverity] = None,
                         category: Optional[ErrorCategory] = None) -> List[ErrorInfo]:
        """Get error history with optional filtering"""
        with self.lock:
            errors = self.error_history.copy()
        
        # Apply filters
        if severity:
            errors = [e for e in errors if e.severity == severity]
        
        if category:
            errors = [e for e in errors if e.category == category]
        
        # Sort by timestamp (newest first)
        errors.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            errors = errors[:limit]
        
        return errors
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self.lock:
            total_errors = len(self.error_history)
            
            # Count by severity
            severity_counts = {}
            for severity in ErrorSeverity:
                severity_counts[severity.value] = sum(1 for e in self.error_history 
                                                    if e.severity == severity)
            
            # Count by category
            category_counts = {}
            for category in ErrorCategory:
                category_counts[category.value] = sum(1 for e in self.error_history 
                                                    if e.category == category)
            
            # Recent errors (last 24 hours)
            cutoff_time = datetime.now() - timedelta(days=1)
            recent_errors = sum(1 for e in self.error_history 
                               if e.timestamp > cutoff_time)
            
            return {
                "total_errors": total_errors,
                "severity_counts": severity_counts,
                "category_counts": category_counts,
                "recent_errors_24h": recent_errors,
                "recovery_strategies": list(self.recovery_strategies.keys())
            }
    
    def clear_error_history(self):
        """Clear error history"""
        with self.lock:
            self.error_history.clear()
            self._save_error_history()
        logger.info("Error history cleared")
    
    def _register_default_strategies(self):
        """Register default recovery strategies"""
        
        def retry_network_error(error_info: ErrorInfo):
            """Retry strategy for network errors"""
            if error_info.retry_count < error_info.max_retries:
                delay = min(2 ** error_info.retry_count, 10)  # Exponential backoff
                time.sleep(delay)
                error_info.retry_count += 1
                return True
            return False
        
        def retry_api_error(error_info: ErrorInfo):
            """Retry strategy for API errors"""
            if error_info.retry_count < error_info.max_retries:
                delay = min(2 ** error_info.retry_count, 30)  # Exponential backoff
                time.sleep(delay)
                error_info.retry_count += 1
                return True
            return False
        
        def cleanup_memory_error(error_info: ErrorInfo):
            """Cleanup strategy for memory errors"""
            import gc
            gc.collect()
            return True
        
        def handle_file_error(error_info: ErrorInfo):
            """File error handling strategy"""
            context = error_info.context
            if "file_path" in context:
                file_path = context["file_path"]
                # Check if file exists
                if not Path(file_path).exists():
                    logger.error(f"File not found: {file_path}")
                    return False
            return False
        
        # Register strategies
        self.register_recovery_strategy("ConnectionError", retry_network_error)
        self.register_recovery_strategy("TimeoutError", retry_network_error)
        self.register_recovery_strategy("HTTPError", retry_api_error)
        self.register_recovery_strategy("RequestException", retry_api_error)
        self.register_recovery_strategy("MemoryError", cleanup_memory_error)
        self.register_recovery_strategy("FileNotFoundError", handle_file_error)
        self.register_recovery_strategy("PermissionError", handle_file_error)
    
    def _attempt_recovery(self, error_info: ErrorInfo):
        """Attempt to recover from error"""
        strategy = self.recovery_strategies.get(error_info.error_type)
        if strategy:
            try:
                success = strategy(error_info)
                if success:
                    error_info.is_handled = True
                    logger.info(f"Error recovered using strategy: {error_info.error_type}")
                else:
                    logger.warning(f"Recovery strategy failed for: {error_info.error_type}")
            except Exception as recovery_error:
                logger.error(f"Recovery strategy failed with error: {recovery_error}")
        
        # Update project progress if needed
        if error_info.project_id and error_info.step_id:
            if error_info.is_handled:
                progress_manager.retry_step(error_info.project_id, error_info.step_id)
            else:
                progress_manager.fail_step(
                    error_info.project_id, 
                    error_info.step_id, 
                    error_info.error_message
                )
    
    def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level"""
        log_message = f"Error [{error_info.error_id}]: {error_info.error_type} - {error_info.error_message}"
        
        if error_info.context:
            log_message += f" - Context: {error_info.context}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Log stack trace for high and critical errors
        if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            if error_info.stack_trace:
                logger.error(f"Stack trace for error {error_info.error_id}:\n{error_info.stack_trace}")
    
    def _notify_error_callbacks(self, error_info: ErrorInfo):
        """Notify error callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                logger.error(f"Error callback failed: {e}")
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_part = str(int(time.time() * 1000) % 10000)
        return f"ERR_{timestamp}_{random_part}"
    
    def _save_error_history(self):
        """Save error history to cache"""
        try:
            error_data = [error.to_dict() for error in self.error_history]
            
            from .cache_manager import cache_manager
            cache_manager.put(
                "error_history",
                error_data,
                ttl=30 * 24 * 3600,  # 30 days
                metadata={"type": "error_history", "timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            logger.error(f"Failed to save error history: {e}")
    
    def _load_error_history(self):
        """Load error history from cache"""
        try:
            from .cache_manager import cache_manager
            error_data = cache_manager.get("error_history")
            if error_data:
                self.error_history = [ErrorInfo.from_dict(data) for data in error_data]
                logger.info(f"Loaded {len(self.error_history)} error records")
        except Exception as e:
            logger.error(f"Failed to load error history: {e}")


# Global error handler instance
error_handler = ErrorHandler()


def handle_exceptions(severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    category: ErrorCategory = ErrorCategory.UNKNOWN,
                    recovery_action: RecoveryAction = RecoveryAction.LOG_ONLY):
    """Decorator to handle exceptions in functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Extract context from function arguments
                context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
                
                # Handle error
                error_handler.handle_error(
                    error=e,
                    context=context,
                    severity=severity,
                    category=category,
                    recovery_action=recovery_action
                )
                raise
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, 
                    backoff_factor: float = 2.0, 
                    exceptions: tuple = (Exception,)):
    """Decorator to retry functions on failure"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        # Last attempt failed, handle error
                        error_handler.handle_error(
                            error=e,
                            context={"function": func.__name__, "attempts": max_retries + 1},
                            severity=ErrorSeverity.HIGH,
                            category=ErrorCategory.PROCESSING
                        )
                        raise
                    
                    # Wait before retry
                    wait_time = delay * (backoff_factor ** attempt)
                    logger.warning(f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__} in {wait_time}s")
                    time.sleep(wait_time)
        return wrapper
    return decorator
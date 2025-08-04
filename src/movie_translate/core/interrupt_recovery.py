"""
Interrupt recovery mechanism for Movie Translate
Handles application interruptions and allows users to resume work from where they left off
"""

import json
import pickle
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import threading
import atexit
import signal
import sys

from movie_translate.core import logger, settings
from movie_translate.core.error_handler import ErrorSeverity, error_handler


class InterruptRecovery:
    """Handles interrupt recovery for the application"""
    
    def __init__(self):
        self.recovery_file = settings.get_temp_path() / "recovery.pkl"
        self.backup_file = settings.get_temp_path() / "recovery_backup.pkl"
        self.lock_file = settings.get_temp_path() / "recovery.lock"
        self.auto_save_interval = 30  # seconds
        self.current_state = None
        self.last_save_time = None
        self.auto_save_timer = None
        self.is_running = False
        
        # Register signal handlers
        self._register_signal_handlers()
        
        # Register exit handler
        atexit.register(self._cleanup)
        
        logger.info("Interrupt recovery mechanism initialized")
    
    def _register_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""
        if sys.platform != "win32":
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        else:
            # Windows-specific handling
            signal.signal(signal.SIGBREAK, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        logger.warning(f"Received signal {signum}, initiating graceful shutdown")
        self.save_state()
        sys.exit(0)
    
    def _cleanup(self):
        """Cleanup on application exit"""
        if self.is_running:
            self.save_state()
            self._release_lock()
    
    def _acquire_lock(self) -> bool:
        """Acquire lock file to prevent multiple instances"""
        try:
            if self.lock_file.exists():
                # Check if lock is stale (older than 5 minutes)
                lock_time = datetime.fromtimestamp(self.lock_file.stat().st_mtime)
                if (datetime.now() - lock_time).total_seconds() > 300:
                    self.lock_file.unlink()
                else:
                    return False
            
            self.lock_file.write_text(str(datetime.now().timestamp()))
            return True
        except Exception as e:
            logger.error(f"Failed to acquire lock: {e}")
            return False
    
    def _release_lock(self):
        """Release lock file"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception as e:
            logger.error(f"Failed to release lock: {e}")
    
    def start_auto_save(self):
        """Start auto-save timer"""
        if self.auto_save_timer is None:
            self.auto_save_timer = threading.Timer(self.auto_save_interval, self._auto_save)
            self.auto_save_timer.start()
            self.is_running = True
            logger.info("Auto-save started")
    
    def stop_auto_save(self):
        """Stop auto-save timer"""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None
            self.is_running = False
            logger.info("Auto-save stopped")
    
    def _auto_save(self):
        """Auto-save current state"""
        if self.current_state:
            self.save_state()
        
        # Schedule next auto-save
        if self.is_running:
            self.auto_save_timer = threading.Timer(self.auto_save_interval, self._auto_save)
            self.auto_save_timer.start()
    
    def save_state(self, state: Optional[Dict[str, Any]] = None):
        """Save current state to recovery file"""
        try:
            if state is not None:
                self.current_state = state
            elif self.current_state is None:
                logger.warning("No state to save")
                return
            
            # Create backup of existing file
            if self.recovery_file.exists():
                shutil.copy2(self.recovery_file, self.backup_file)
            
            # Save state with metadata
            save_data = {
                'state': self.current_state,
                'timestamp': datetime.now().isoformat(),
                'version': settings.__version__,
                'platform': sys.platform
            }
            
            # Use pickle for complex objects
            with open(self.recovery_file, 'wb') as f:
                pickle.dump(save_data, f)
            
            self.last_save_time = datetime.now()
            logger.info(f"State saved to {self.recovery_file}")
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "save_recovery_state"},
                severity=ErrorSeverity.ERROR
            )
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load state from recovery file"""
        try:
            if not self.recovery_file.exists():
                logger.info("No recovery file found")
                return None
            
            # Check lock
            if not self._acquire_lock():
                logger.warning("Could not acquire lock for recovery")
                return None
            
            # Load state
            with open(self.recovery_file, 'rb') as f:
                save_data = pickle.load(f)
            
            # Validate state
            if not self._validate_state(save_data):
                logger.warning("Invalid recovery state")
                return None
            
            self.current_state = save_data['state']
            logger.info(f"State loaded from {self.recovery_file}")
            
            return self.current_state
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "load_recovery_state"},
                severity=ErrorSeverity.ERROR
            )
            
            # Try to load from backup
            if self.backup_file.exists():
                try:
                    logger.info("Attempting to load from backup")
                    with open(self.backup_file, 'rb') as f:
                        save_data = pickle.load(f)
                    
                    if self._validate_state(save_data):
                        self.current_state = save_data['state']
                        logger.info("State loaded from backup")
                        return self.current_state
                        
                except Exception as backup_e:
                    logger.error(f"Failed to load backup: {backup_e}")
            
            return None
    
    def _validate_state(self, save_data: Dict[str, Any]) -> bool:
        """Validate loaded state"""
        try:
            # Check required fields
            required_fields = ['state', 'timestamp', 'version']
            for field in required_fields:
                if field not in save_data:
                    return False
            
            # Check timestamp (not too old, e.g., older than 7 days)
            timestamp = datetime.fromisoformat(save_data['timestamp'])
            if (datetime.now() - timestamp).days > 7:
                logger.warning("Recovery state is too old")
                return False
            
            # Check version compatibility
            saved_version = save_data['version']
            current_version = settings.__version__
            if saved_version != current_version:
                logger.warning(f"Version mismatch: {saved_version} vs {current_version}")
                # Could implement version migration here
            
            return True
            
        except Exception as e:
            logger.error(f"State validation failed: {e}")
            return False
    
    def has_recovery_state(self) -> bool:
        """Check if recovery state exists"""
        return self.recovery_file.exists() or self.backup_file.exists()
    
    def get_recovery_info(self) -> Dict[str, Any]:
        """Get information about available recovery state"""
        info = {
            'has_state': False,
            'timestamp': None,
            'version': None,
            'age': None
        }
        
        try:
            if self.recovery_file.exists():
                with open(self.recovery_file, 'rb') as f:
                    save_data = pickle.load(f)
                
                info['has_state'] = True
                info['timestamp'] = save_data['timestamp']
                info['version'] = save_data['version']
                
                timestamp = datetime.fromisoformat(save_data['timestamp'])
                info['age'] = (datetime.now() - timestamp).total_seconds()
                
        except Exception as e:
            logger.error(f"Failed to get recovery info: {e}")
        
        return info
    
    def clear_recovery_state(self):
        """Clear recovery state"""
        try:
            if self.recovery_file.exists():
                self.recovery_file.unlink()
            
            if self.backup_file.exists():
                self.backup_file.unlink()
            
            self.current_state = None
            self.last_save_time = None
            
            logger.info("Recovery state cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear recovery state: {e}")
    
    def update_project_state(self, project_data: Dict[str, Any]):
        """Update project state in recovery"""
        if self.current_state is None:
            self.current_state = {}
        
        self.current_state['project'] = project_data
        self.current_state['last_updated'] = datetime.now().isoformat()
        
        # Auto-save if running
        if self.is_running:
            self.save_state()
    
    def update_step_state(self, step: int, step_data: Dict[str, Any]):
        """Update step state in recovery"""
        if self.current_state is None:
            self.current_state = {}
        
        if 'steps' not in self.current_state:
            self.current_state['steps'] = {}
        
        self.current_state['steps'][step] = {
            'data': step_data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.current_state['last_updated'] = datetime.now().isoformat()
        
        # Auto-save if running
        if self.is_running:
            self.save_state()
    
    def get_project_state(self) -> Optional[Dict[str, Any]]:
        """Get project state from recovery"""
        if self.current_state and 'project' in self.current_state:
            return self.current_state['project']
        return None
    
    def get_step_state(self, step: int) -> Optional[Dict[str, Any]]:
        """Get step state from recovery"""
        if self.current_state and 'steps' in self.current_state:
            step_info = self.current_state['steps'].get(step)
            if step_info:
                return step_info['data']
        return None
    
    def create_checkpoint(self, checkpoint_name: str):
        """Create a named checkpoint"""
        try:
            checkpoint_file = settings.get_temp_path() / f"checkpoint_{checkpoint_name}.pkl"
            
            checkpoint_data = {
                'state': self.current_state,
                'checkpoint_name': checkpoint_name,
                'timestamp': datetime.now().isoformat(),
                'version': settings.__version__
            }
            
            with open(checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            
            logger.info(f"Checkpoint '{checkpoint_name}' created")
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
    
    def load_checkpoint(self, checkpoint_name: str) -> bool:
        """Load a named checkpoint"""
        try:
            checkpoint_file = settings.get_temp_path() / f"checkpoint_{checkpoint_name}.pkl"
            
            if not checkpoint_file.exists():
                logger.warning(f"Checkpoint '{checkpoint_name}' not found")
                return False
            
            with open(checkpoint_file, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            if self._validate_state(checkpoint_data):
                self.current_state = checkpoint_data['state']
                logger.info(f"Checkpoint '{checkpoint_name}' loaded")
                return True
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
        
        return False
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List available checkpoints"""
        checkpoints = []
        
        try:
            temp_path = settings.get_temp_path()
            for file in temp_path.glob("checkpoint_*.pkl"):
                try:
                    with open(file, 'rb') as f:
                        checkpoint_data = pickle.load(f)
                    
                    checkpoints.append({
                        'name': checkpoint_data['checkpoint_name'],
                        'timestamp': checkpoint_data['timestamp'],
                        'version': checkpoint_data['version']
                    })
                except Exception:
                    continue
            
            # Sort by timestamp
            checkpoints.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list checkpoints: {e}")
        
        return checkpoints
    
    def delete_checkpoint(self, checkpoint_name: str):
        """Delete a named checkpoint"""
        try:
            checkpoint_file = settings.get_temp_path() / f"checkpoint_{checkpoint_name}.pkl"
            
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                logger.info(f"Checkpoint '{checkpoint_name}' deleted")
            
        except Exception as e:
            logger.error(f"Failed to delete checkpoint: {e}")


# Global instance
interrupt_recovery = InterruptRecovery()


def get_interrupt_recovery() -> InterruptRecovery:
    """Get the global interrupt recovery instance"""
    return interrupt_recovery
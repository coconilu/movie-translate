"""
Progress management module for Movie Translate
"""

import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
import json

from .config import settings
from .logger import logger
from .cache_manager import cache_manager


class StepStatus(Enum):
    """Processing step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ProcessingStep(Enum):
    """Processing pipeline steps"""
    FILE_IMPORT = "file_import"
    AUDIO_EXTRACTION = "audio_extraction"
    SPEECH_RECOGNITION = "speech_recognition"
    TRANSLATION = "translation"
    CHARACTER_IDENTIFICATION = "character_identification"
    VOICE_CLONING = "voice_cloning"
    VIDEO_SYNTHESIS = "video_synthesis"


@dataclass
class StepProgress:
    """Progress information for a single step"""
    step_id: str
    step_name: str
    status: StepStatus
    progress: float = 0.0  # 0.0 to 1.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "status": self.status.value,
            "progress": self.progress,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepProgress':
        """Create from dictionary"""
        return cls(
            step_id=data["step_id"],
            step_name=data["step_name"],
            status=StepStatus(data["status"]),
            progress=data["progress"],
            start_time=datetime.fromisoformat(data["start_time"]) if data["start_time"] else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            duration=data["duration"],
            error_message=data["error_message"],
            retry_count=data["retry_count"],
            metadata=data["metadata"]
        )


@dataclass
class ProjectProgress:
    """Progress information for a complete project"""
    project_id: str
    project_name: str
    file_path: str
    total_steps: int
    completed_steps: int = 0
    current_step: Optional[str] = None
    overall_progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    status: StepStatus = StepStatus.PENDING
    steps: Dict[str, StepProgress] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_overall_progress(self):
        """Update overall progress based on step progress"""
        if not self.steps:
            self.overall_progress = 0.0
            return
        
        total_progress = sum(step.progress for step in self.steps.values())
        self.overall_progress = total_progress / len(self.steps)
        
        # Count completed steps
        self.completed_steps = sum(1 for step in self.steps.values() 
                                 if step.status == StepStatus.COMPLETED)
        
        # Update current step
        running_steps = [step for step in self.steps.values() 
                        if step.status == StepStatus.RUNNING]
        self.current_step = running_steps[0].step_id if running_steps else None
        
        # Update project status
        if self.completed_steps == len(self.steps):
            self.status = StepStatus.COMPLETED
            self.end_time = datetime.now()
        elif any(step.status == StepStatus.FAILED for step in self.steps.values()):
            self.status = StepStatus.FAILED
        elif any(step.status == StepStatus.CANCELLED for step in self.steps.values()):
            self.status = StepStatus.CANCELLED
        elif any(step.status == StepStatus.PAUSED for step in self.steps.values()):
            self.status = StepStatus.PAUSED
        elif self.current_step:
            self.status = StepStatus.RUNNING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "file_path": self.file_path,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "current_step": self.current_step,
            "overall_progress": self.overall_progress,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "status": self.status.value,
            "steps": {k: v.to_dict() for k, v in self.steps.items()},
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectProgress':
        """Create from dictionary"""
        return cls(
            project_id=data["project_id"],
            project_name=data["project_name"],
            file_path=data["file_path"],
            total_steps=data["total_steps"],
            completed_steps=data["completed_steps"],
            current_step=data["current_step"],
            overall_progress=data["overall_progress"],
            start_time=datetime.fromisoformat(data["start_time"]) if data["start_time"] else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            estimated_completion=datetime.fromisoformat(data["estimated_completion"]) if data["estimated_completion"] else None,
            status=StepStatus(data["status"]),
            steps={k: StepProgress.from_dict(v) for k, v in data["steps"].items()},
            metadata=data["metadata"]
        )


class ProgressManager:
    """Progress management system for Movie Translate"""
    
    def __init__(self):
        self.projects: Dict[str, ProjectProgress] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.lock = threading.Lock()
        self.auto_save = True
        
        # Load saved progress
        self._load_progress()
    
    def create_project(self, project_id: str, project_name: str, file_path: str) -> ProjectProgress:
        """Create a new project progress tracker"""
        with self.lock:
            if project_id in self.projects:
                return self.projects[project_id]
            
            project = ProjectProgress(
                project_id=project_id,
                project_name=project_name,
                file_path=file_path,
                total_steps=len(ProcessingStep),
                start_time=datetime.now()
            )
            
            # Initialize steps
            for step in ProcessingStep:
                step_progress = StepProgress(
                    step_id=step.value,
                    step_name=self._get_step_display_name(step),
                    status=StepStatus.PENDING
                )
                project.steps[step.value] = step_progress
            
            self.projects[project_id] = project
            self._save_progress()
            
            logger.info(f"Created project progress: {project_id}")
            return project
    
    def get_project(self, project_id: str) -> Optional[ProjectProgress]:
        """Get project progress"""
        with self.lock:
            return self.projects.get(project_id)
    
    def update_step_progress(self, project_id: str, step_id: str, progress: float, 
                           metadata: Optional[Dict[str, Any]] = None):
        """Update step progress"""
        with self.lock:
            project = self.projects.get(project_id)
            if not project:
                return
            
            step = project.steps.get(step_id)
            if not step:
                return
            
            # Update step
            step.progress = max(0.0, min(1.0, progress))
            if metadata:
                step.metadata.update(metadata)
            
            # Update project
            project.update_overall_progress()
            self._save_progress()
            
            # Notify callbacks
            self._notify_callbacks(project_id, "step_progress", {
                "step_id": step_id,
                "progress": step.progress,
                "metadata": metadata
            })
    
    def start_step(self, project_id: str, step_id: str):
        """Start a step"""
        with self.lock:
            project = self.projects.get(project_id)
            if not project:
                return
            
            step = project.steps.get(step_id)
            if not step:
                return
            
            step.status = StepStatus.RUNNING
            step.start_time = datetime.now()
            step.error_message = None
            
            # Update project
            project.update_overall_progress()
            self._save_progress()
            
            logger.log_processing_step(step_id, "started")
            self._notify_callbacks(project_id, "step_started", {"step_id": step_id})
    
    def complete_step(self, project_id: str, step_id: str):
        """Complete a step"""
        with self.lock:
            project = self.projects.get(project_id)
            if not project:
                return
            
            step = project.steps.get(step_id)
            if not step:
                return
            
            step.status = StepStatus.COMPLETED
            step.progress = 1.0
            step.end_time = datetime.now()
            
            if step.start_time:
                step.duration = (step.end_time - step.start_time).total_seconds()
            
            # Update project
            project.update_overall_progress()
            self._save_progress()
            
            logger.log_processing_step(step_id, "completed", {
                "duration": step.duration,
                "retry_count": step.retry_count
            })
            self._notify_callbacks(project_id, "step_completed", {"step_id": step_id})
    
    def fail_step(self, project_id: str, step_id: str, error_message: str):
        """Fail a step"""
        with self.lock:
            project = self.projects.get(project_id)
            if not project:
                return
            
            step = project.steps.get(step_id)
            if not step:
                return
            
            step.status = StepStatus.FAILED
            step.end_time = datetime.now()
            step.error_message = error_message
            
            if step.start_time:
                step.duration = (step.end_time - step.start_time).total_seconds()
            
            # Update project
            project.update_overall_progress()
            self._save_progress()
            
            logger.log_processing_step(step_id, "failed", {
                "error": error_message,
                "duration": step.duration
            })
            self._notify_callbacks(project_id, "step_failed", {
                "step_id": step_id,
                "error": error_message
            })
    
    def pause_step(self, project_id: str, step_id: str):
        """Pause a step"""
        with self.lock:
            project = self.projects.get(project_id)
            if not project:
                return
            
            step = project.steps.get(step_id)
            if not step:
                return
            
            step.status = StepStatus.PAUSED
            
            # Update project
            project.update_overall_progress()
            self._save_progress()
            
            logger.log_processing_step(step_id, "paused")
            self._notify_callbacks(project_id, "step_paused", {"step_id": step_id})
    
    def cancel_step(self, project_id: str, step_id: str):
        """Cancel a step"""
        with self.lock:
            project = self.projects.get(project_id)
            if not project:
                return
            
            step = project.steps.get(step_id)
            if not step:
                return
            
            step.status = StepStatus.CANCELLED
            step.end_time = datetime.now()
            
            if step.start_time:
                step.duration = (step.end_time - step.start_time).total_seconds()
            
            # Update project
            project.update_overall_progress()
            self._save_progress()
            
            logger.log_processing_step(step_id, "cancelled")
            self._notify_callbacks(project_id, "step_cancelled", {"step_id": step_id})
    
    def skip_step(self, project_id: str, step_id: str):
        """Skip a step"""
        with self.lock:
            project = self.projects.get(project_id)
            if not project:
                return
            
            step = project.steps.get(step_id)
            if not step:
                return
            
            step.status = StepStatus.SKIPPED
            step.progress = 1.0
            
            # Update project
            project.update_overall_progress()
            self._save_progress()
            
            logger.log_processing_step(step_id, "skipped")
            self._notify_callbacks(project_id, "step_skipped", {"step_id": step_id})
    
    def retry_step(self, project_id: str, step_id: str):
        """Retry a step"""
        with self.lock:
            project = self.projects.get(project_id)
            if not project:
                return
            
            step = project.steps.get(step_id)
            if not step:
                return
            
            step.status = StepStatus.PENDING
            step.progress = 0.0
            step.start_time = None
            step.end_time = None
            step.duration = None
            step.error_message = None
            step.retry_count += 1
            
            # Update project
            project.update_overall_progress()
            self._save_progress()
            
            logger.log_processing_step(step_id, "retry", {
                "retry_count": step.retry_count
            })
            self._notify_callbacks(project_id, "step_retry", {"step_id": step_id})
    
    def add_callback(self, project_id: str, callback: Callable):
        """Add progress callback"""
        with self.lock:
            if project_id not in self.callbacks:
                self.callbacks[project_id] = []
            self.callbacks[project_id].append(callback)
    
    def remove_callback(self, project_id: str, callback: Callable):
        """Remove progress callback"""
        with self.lock:
            if project_id in self.callbacks:
                try:
                    self.callbacks[project_id].remove(callback)
                except ValueError:
                    pass
    
    def _notify_callbacks(self, project_id: str, event_type: str, data: Dict[str, Any]):
        """Notify callbacks of progress updates"""
        if project_id in self.callbacks:
            for callback in self.callbacks[project_id]:
                try:
                    callback(event_type, data)
                except Exception as e:
                    logger.error(f"Progress callback error: {e}")
    
    def _save_progress(self):
        """Save progress to cache"""
        if not self.auto_save:
            return
        
        try:
            progress_data = {
                project_id: project.to_dict() 
                for project_id, project in self.projects.items()
            }
            
            cache_manager.put(
                "progress_data",
                progress_data,
                ttl=30 * 24 * 3600,  # 30 days
                metadata={"type": "progress", "timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def _load_progress(self):
        """Load progress from cache"""
        try:
            progress_data = cache_manager.get("progress_data")
            if progress_data:
                self.projects = {
                    project_id: ProjectProgress.from_dict(project_data)
                    for project_id, project_data in progress_data.items()
                }
                logger.info(f"Loaded progress for {len(self.projects)} projects")
        except Exception as e:
            logger.error(f"Failed to load progress: {e}")
    
    def cleanup_completed_projects(self, days_old: int = 7):
        """Clean up completed projects older than specified days"""
        cutoff_time = datetime.now() - timedelta(days=days_old)
        
        with self.lock:
            projects_to_remove = []
            
            for project_id, project in self.projects.items():
                if (project.status == StepStatus.COMPLETED and 
                    project.end_time and 
                    project.end_time < cutoff_time):
                    projects_to_remove.append(project_id)
            
            for project_id in projects_to_remove:
                del self.projects[project_id]
                logger.info(f"Cleaned up completed project: {project_id}")
            
            if projects_to_remove:
                self._save_progress()
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Get project statistics"""
        with self.lock:
            total_projects = len(self.projects)
            completed_projects = sum(1 for p in self.projects.values() 
                                   if p.status == StepStatus.COMPLETED)
            running_projects = sum(1 for p in self.projects.values() 
                                 if p.status == StepStatus.RUNNING)
            failed_projects = sum(1 for p in self.projects.values() 
                                if p.status == StepStatus.FAILED)
            
            return {
                "total_projects": total_projects,
                "completed_projects": completed_projects,
                "running_projects": running_projects,
                "failed_projects": failed_projects,
                "auto_save": self.auto_save
            }
    
    def _get_step_display_name(self, step: ProcessingStep) -> str:
        """Get display name for step"""
        names = {
            ProcessingStep.FILE_IMPORT: "文件导入",
            ProcessingStep.AUDIO_EXTRACTION: "音频提取",
            ProcessingStep.SPEECH_RECOGNITION: "语音识别",
            ProcessingStep.TRANSLATION: "文本翻译",
            ProcessingStep.CHARACTER_IDENTIFICATION: "角色识别",
            ProcessingStep.VOICE_CLONING: "声音克隆",
            ProcessingStep.VIDEO_SYNTHESIS: "视频合成"
        }
        return names.get(step, step.value)


# Global progress manager instance
progress_manager = ProgressManager()
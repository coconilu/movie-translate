"""
FastAPI backend service for Movie Translate
"""

import asyncio
import json
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import numpy as np

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity, cache_manager
from ..services import (
    audio_processing_service, speech_recognition_service, translation_service,
    character_identification_service, voice_cloning_service, video_synthesis_service
)
from ..utils.file_utils import FileUtils
from ..core.progress_manager import ProcessingStep, StepStatus


# Pydantic models for API requests/responses
class ProjectInfo(BaseModel):
    """Project information model"""
    project_id: str
    name: str
    created_at: datetime
    status: str
    progress: float
    current_step: str
    total_steps: int
    source_file: Optional[str] = None
    output_file: Optional[str] = None


class ProcessingRequest(BaseModel):
    """Processing request model"""
    project_id: str
    source_file_path: str
    target_language: str = "en"
    source_language: str = "auto"
    output_path: Optional[str] = None
    settings: Dict[str, Any] = {}


class ProcessingStatus(BaseModel):
    """Processing status model"""
    project_id: str
    status: str
    current_step: str
    progress: float
    message: str
    error: Optional[str] = None
    estimated_time_remaining: Optional[float] = None


class CharacterInfo(BaseModel):
    """Character information model"""
    character_id: str
    character_name: str
    segments_count: int
    avg_duration: float
    language: str
    created_at: datetime
    voice_features: Optional[List[float]] = None


class TranslationRequest(BaseModel):
    """Translation request model"""
    text: str
    source_lang: str
    target_lang: str
    context: Optional[str] = None


class VoiceCloningRequest(BaseModel):
    """Voice cloning request model"""
    character_id: str
    text: str
    output_path: str
    service: str = "auto"


class AudioAnalysisResult(BaseModel):
    """Audio analysis result model"""
    segments: List[Dict[str, Any]]
    language: str
    duration: float
    sample_rate: int
    channels: int


# Global state
active_projects: Dict[str, Dict[str, Any]] = {}
processing_tasks: Dict[str, asyncio.Task] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("FastAPI backend starting up...")
    
    # Initialize services
    try:
        await audio_processing_service._initialize()
        await speech_recognition_service._initialize()
        await translation_service._initialize()
        await character_identification_service._initialize()
        await voice_cloning_service._initialize()
        await video_synthesis_service._initialize()
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Service initialization failed: {e}")
        raise
    
    yield
    
    logger.info("FastAPI backend shutting down...")
    
    # Cancel active processing tasks
    for task in processing_tasks.values():
        if not task.done():
            task.cancel()
    
    # Wait for tasks to complete
    if processing_tasks:
        await asyncio.gather(*processing_tasks.values(), return_exceptions=True)


# Create FastAPI app
app = FastAPI(
    title="Movie Translate API",
    description="AI-powered movie translation and dubbing system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# Project management endpoints
@app.post("/projects", response_model=ProjectInfo)
async def create_project(name: str, source_file_path: str) -> ProjectInfo:
    """Create a new project"""
    try:
        project_id = str(uuid.uuid4())
        
        # Validate source file
        if not Path(source_file_path).exists():
            raise HTTPException(status_code=404, detail="Source file not found")
        
        # Create project info
        project = {
            "project_id": project_id,
            "name": name,
            "created_at": datetime.now(),
            "status": "created",
            "progress": 0.0,
            "current_step": "file_import",
            "total_steps": 6,
            "source_file": source_file_path,
            "output_file": None,
            "settings": {}
        }
        
        active_projects[project_id] = project
        
        logger.info(f"Project created: {project_id}")
        return ProjectInfo(**project)
        
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"operation": "create_project"},
            category=ErrorCategory.API,
            severity=ErrorSeverity.HIGH
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}", response_model=ProjectInfo)
async def get_project(project_id: str):
    """Get project information"""
    try:
        if project_id not in active_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ProjectInfo(**active_projects[project_id])
        
    except HTTPException:
        raise
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"project_id": project_id},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects")
async def list_projects() -> List[ProjectInfo]:
    """List all projects"""
    try:
        return [ProjectInfo(**project) for project in active_projects.values()]
        
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"operation": "list_projects"},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        if project_id not in active_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Cancel any active processing
        if project_id in processing_tasks:
            processing_tasks[project_id].cancel()
            del processing_tasks[project_id]
        
        del active_projects[project_id]
        
        logger.info(f"Project deleted: {project_id}")
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"project_id": project_id},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


# Processing endpoints
@app.post("/projects/{project_id}/process")
async def start_processing(project_id: str, request: ProcessingRequest):
    """Start processing a project"""
    try:
        if project_id not in active_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if project_id in processing_tasks:
            raise HTTPException(status_code=400, detail="Processing already in progress")
        
        # Update project status
        project = active_projects[project_id]
        project.update({
            "status": "processing",
            "progress": 0.0,
            "current_step": "audio_processing"
        })
        
        # Start processing task
        task = asyncio.create_task(
            process_movie_translation(project_id, request)
        )
        processing_tasks[project_id] = task
        
        logger.info(f"Processing started for project: {project_id}")
        return {"message": "Processing started", "project_id": project_id}
        
    except HTTPException:
        raise
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"project_id": project_id},
            category=ErrorCategory.API,
            severity=ErrorSeverity.HIGH
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}/status", response_model=ProcessingStatus)
async def get_processing_status(project_id: str):
    """Get processing status"""
    try:
        if project_id not in active_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = active_projects[project_id]
        
        # Check if task is completed
        if project_id in processing_tasks:
            task = processing_tasks[project_id]
            if task.done():
                try:
                    result = task.result()
                    project.update({
                        "status": "completed",
                        "progress": 1.0,
                        "current_step": "completed",
                        "output_file": result.get("output_file")
                    })
                except Exception as e:
                    project.update({
                        "status": "failed",
                        "error": str(e)
                    })
                del processing_tasks[project_id]
        
        return ProcessingStatus(
            project_id=project_id,
            status=project["status"],
            current_step=project["current_step"],
            progress=project["progress"],
            message=f"Processing {project['current_step']}",
            error=project.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"project_id": project_id},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/cancel")
async def cancel_processing(project_id: str):
    """Cancel processing"""
    try:
        if project_id not in active_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if project_id in processing_tasks:
            task = processing_tasks[project_id]
            task.cancel()
            del processing_tasks[project_id]
            
            # Update project status
            active_projects[project_id].update({
                "status": "cancelled",
                "current_step": "cancelled"
            })
            
            logger.info(f"Processing cancelled for project: {project_id}")
            return {"message": "Processing cancelled"}
        else:
            raise HTTPException(status_code=400, detail="No active processing")
        
    except HTTPException:
        raise
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"project_id": project_id},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


# Character management endpoints
@app.get("/projects/{project_id}/characters", response_model=List[CharacterInfo])
async def get_project_characters(project_id: str):
    """Get characters for a project"""
    try:
        if project_id not in active_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = active_projects[project_id]
        characters = project.get("characters", [])
        
        return [CharacterInfo(**char) for char in characters]
        
    except HTTPException:
        raise
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"project_id": project_id},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/projects/{project_id}/characters/{character_id}")
async def update_character_name(project_id: str, character_id: str, name: str):
    """Update character name"""
    try:
        if project_id not in active_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = active_projects[project_id]
        characters = project.get("characters", [])
        
        # Find and update character
        for char in characters:
            if char["character_id"] == character_id:
                char["character_name"] = name
                break
        else:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Also update in character identification service
        await character_identification_service.update_character_name(character_id, name)
        
        logger.info(f"Character name updated: {character_id} -> {name}")
        return {"message": "Character name updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"project_id": project_id, "character_id": character_id},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


# Translation endpoints
@app.post("/translate", response_model=Dict[str, Any])
async def translate_text(request: TranslationRequest):
    """Translate text"""
    try:
        result = await translation_service.translate_text(
            request.text, request.source_lang, request.target_lang
        )
        
        return {
            "original_text": result.original_text,
            "translated_text": result.translated_text,
            "source_lang": result.source_lang,
            "target_lang": result.target_lang,
            "confidence": result.confidence,
            "alternatives": result.alternatives
        }
        
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"text": request.text[:50]},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


# File upload/download endpoints
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file"""
    try:
        # Create upload directory
        upload_dir = settings.get_temp_path() / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        filename = f"{file_id}{file_extension}"
        file_path = upload_dir / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get file info
        file_info = await FileUtils.get_file_info(str(file_path))
        
        logger.info(f"File uploaded: {filename}")
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": file_info.get("file_size", 0),
            "file_type": file_info.get("file_type", "unknown"),
            "duration": file_info.get("duration", 0)
        }
        
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"filename": file.filename if file else "unknown"},
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.HIGH
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download a file"""
    try:
        # Find file
        upload_dir = settings.get_temp_path() / "uploads"
        file_pattern = f"{file_id}.*"
        
        for file_path in upload_dir.glob(file_pattern):
            if file_path.exists():
                return FileResponse(
                    path=str(file_path),
                    filename=file_path.name,
                    media_type=mimetypes.guess_type(str(file_path))[0]
                )
        
        raise HTTPException(status_code=404, detail="File not found")
        
    except HTTPException:
        raise
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"file_id": file_id},
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


# Settings endpoints
@app.get("/settings")
async def get_settings():
    """Get application settings"""
    try:
        return {
            "audio": settings.audio.__dict__,
            "translation": settings.translation.__dict__,
            "voice_cloning": settings.voice_cloning.__dict__,
            "video": settings.video.__dict__,
            "cache": settings.cache.__dict__,
            "system": settings.get_system_info()
        }
        
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"operation": "get_settings"},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/settings")
async def update_settings(settings_data: Dict[str, Any]):
    """Update application settings"""
    try:
        # Update settings (simplified version)
        # In production, you would validate and update specific settings
        
        logger.info("Settings updated")
        return {"message": "Settings updated successfully"}
        
    except Exception as e:
        error_handler.handle_error(
            error=e,
            context={"operation": "update_settings"},
            category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM
        )
        raise HTTPException(status_code=500, detail=str(e))


# Main processing function
async def process_movie_translation(project_id: str, request: ProcessingRequest):
    """Process movie translation pipeline"""
    try:
        project = active_projects[project_id]
        
        # Step 1: Audio processing
        project.update({
            "current_step": "audio_processing",
            "progress": 0.1
        })
        
        audio_analysis = await audio_processing_service.analyze_audio(
            request.source_file_path
        )
        
        # Step 2: Speech recognition
        project.update({
            "current_step": "speech_recognition",
            "progress": 0.3
        })
        
        audio_analysis = await speech_recognition_service.transcribe_audio(
            audio_analysis
        )
        
        # Step 3: Character identification
        project.update({
            "current_step": "character_identification",
            "progress": 0.5
        })
        
        audio_analysis = await character_identification_service.identify_characters(
            audio_analysis
        )
        
        # Store characters in project
        characters = character_identification_service.get_all_characters()
        project["characters"] = characters
        
        # Step 4: Translation
        project.update({
            "current_step": "translation",
            "progress": 0.7
        })
        
        audio_analysis = await translation_service.translate_segments(
            audio_analysis, request.target_language
        )
        
        # Step 5: Voice cloning
        project.update({
            "current_step": "voice_cloning",
            "progress": 0.9
        })
        
        output_dir = Path(request.output_path or settings.get_cache_path() / "output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cloned_results = await voice_cloning_service.clone_all_segments(
            audio_analysis, str(output_dir)
        )
        
        # Step 6: Video synthesis
        project.update({
            "current_step": "video_synthesis",
            "progress": 0.95
        })
        
        output_filename = f"translated_{Path(request.source_file_path).stem}.mp4"
        output_path = output_dir / output_filename
        
        video_result = await video_synthesis_service.synthesize_video(
            request.source_file_path, audio_analysis, cloned_results, str(output_path)
        )
        
        # Update project with result
        project.update({
            "status": "completed",
            "progress": 1.0,
            "current_step": "completed",
            "output_file": str(output_path)
        })
        
        logger.info(f"Processing completed for project: {project_id}")
        return {"output_file": str(output_path)}
        
    except Exception as e:
        project.update({
            "status": "failed",
            "error": str(e)
        })
        
        error_handler.handle_error(
            error=e,
            context={"project_id": project_id},
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.HIGH
        )
        raise


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "backend:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.debug,
        log_level="info"
    )
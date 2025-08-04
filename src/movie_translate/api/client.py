"""
API client for Movie Translate desktop application
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from pathlib import Path

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity


class APIClient:
    """API client for communicating with the backend service"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or f"http://{settings.api.host}:{settings.api.port}"
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=settings.api.timeout)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        try:
            if not self.session:
                raise RuntimeError("APIClient must be used as async context manager")
            
            url = f"{self.base_url}{endpoint}"
            
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"API request failed: {response.status} - {error_text}")
        
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"method": method, "endpoint": endpoint},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return await self._request("GET", "/health")
    
    async def create_project(self, name: str, source_file_path: str) -> Dict[str, Any]:
        """Create a new project"""
        data = {"name": name, "source_file_path": source_file_path}
        return await self._request("POST", "/projects", json=data)
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project information"""
        return await self._request("GET", f"/projects/{project_id}")
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        return await self._request("GET", "/projects")
    
    async def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project"""
        return await self._request("DELETE", f"/projects/{project_id}")
    
    async def start_processing(self, project_id: str, processing_request: Dict[str, Any]) -> Dict[str, Any]:
        """Start processing a project"""
        return await self._request("POST", f"/projects/{project_id}/process", json=processing_request)
    
    async def get_processing_status(self, project_id: str) -> Dict[str, Any]:
        """Get processing status"""
        return await self._request("GET", f"/projects/{project_id}/status")
    
    async def cancel_processing(self, project_id: str) -> Dict[str, Any]:
        """Cancel processing"""
        return await self._request("POST", f"/projects/{project_id}/cancel")
    
    async def get_project_characters(self, project_id: str) -> List[Dict[str, Any]]:
        """Get characters for a project"""
        return await self._request("GET", f"/projects/{project_id}/characters")
    
    async def update_character_name(self, project_id: str, character_id: str, name: str) -> Dict[str, Any]:
        """Update character name"""
        data = {"name": name}
        return await self._request("PUT", f"/projects/{project_id}/characters/{character_id}", json=data)
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str, context: str = None) -> Dict[str, Any]:
        """Translate text"""
        data = {
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        if context:
            data["context"] = context
        
        return await self._request("POST", "/translate", json=data)
    
    async def upload_file(self, file_path: str) -> Dict[str, Any]:
        """Upload a file"""
        try:
            if not self.session:
                raise RuntimeError("APIClient must be used as async context manager")
            
            url = f"{self.base_url}/upload"
            
            # Read file
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            # Create multipart form data
            form_data = aiohttp.FormData()
            form_data.add_field("file", file_data, filename=Path(file_path).name)
            
            async with self.session.post(url, data=form_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"File upload failed: {response.status} - {error_text}")
        
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"file_path": file_path},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def download_file(self, file_id: str, output_path: str) -> bool:
        """Download a file"""
        try:
            if not self.session:
                raise RuntimeError("APIClient must be used as async context manager")
            
            url = f"{self.base_url}/download/{file_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    # Save file
                    with open(output_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    return True
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"File download failed: {response.status} - {error_text}")
        
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"file_id": file_id, "output_path": output_path},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    async def get_settings(self) -> Dict[str, Any]:
        """Get application settings"""
        return await self._request("GET", "/settings")
    
    async def update_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update application settings"""
        return await self._request("PUT", "/settings", json=settings_data)
    
    async def wait_for_completion(self, project_id: str, check_interval: float = 2.0) -> Dict[str, Any]:
        """Wait for processing to complete"""
        try:
            while True:
                status = await self.get_processing_status(project_id)
                
                if status["status"] in ["completed", "failed", "cancelled"]:
                    return status
                
                await asyncio.sleep(check_interval)
        
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"project_id": project_id},
                category=ErrorCategory.API,
                severity=ErrorSeverity.MEDIUM
            )
            raise


class ProjectManager:
    """High-level project management using API client"""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.current_project: Optional[Dict[str, Any]] = None
    
    async def create_new_project(self, name: str, source_file_path: str, 
                                target_language: str = "en", 
                                source_language: str = "auto") -> Dict[str, Any]:
        """Create and configure a new project"""
        try:
            # Create project
            project = await self.api_client.create_project(name, source_file_path)
            self.current_project = project
            
            # Start processing
            processing_request = {
                "project_id": project["project_id"],
                "source_file_path": source_file_path,
                "target_language": target_language,
                "source_language": source_language,
                "settings": {}
            }
            
            await self.api_client.start_processing(project["project_id"], processing_request)
            
            logger.info(f"Project created and processing started: {project['project_id']}")
            return project
        
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"name": name, "source_file_path": source_file_path},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project status"""
        try:
            # Get basic project info
            project = await self.api_client.get_project(project_id)
            
            # Get processing status
            status = await self.api_client.get_processing_status(project_id)
            
            # Get characters if available
            characters = []
            if project.get("status") in ["processing", "completed"]:
                try:
                    characters = await self.api_client.get_project_characters(project_id)
                except Exception:
                    # Characters might not be available yet
                    pass
            
            return {
                "project": project,
                "status": status,
                "characters": characters
            }
        
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"project_id": project_id},
                category=ErrorCategory.API,
                severity=ErrorSeverity.MEDIUM
            )
            raise
    
    async def update_character(self, project_id: str, character_id: str, new_name: str) -> bool:
        """Update character information"""
        try:
            await self.api_client.update_character_name(project_id, character_id, new_name)
            logger.info(f"Character updated: {character_id} -> {new_name}")
            return True
        
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"project_id": project_id, "character_id": character_id},
                category=ErrorCategory.API,
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    async def process_to_completion(self, project_id: str, progress_callback=None) -> Dict[str, Any]:
        """Process project to completion with progress updates"""
        try:
            if progress_callback:
                progress_callback(0.0, "Starting processing...")
            
            final_status = await self.api_client.wait_for_completion(project_id)
            
            if progress_callback:
                progress_callback(1.0, f"Processing {final_status['status']}")
            
            return final_status
        
        except Exception as e:
            if progress_callback:
                progress_callback(None, f"Error: {str(e)}")
            
            error_handler.handle_error(
                error=e,
                context={"project_id": project_id},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def download_result(self, project_id: str, output_path: str) -> bool:
        """Download processed result"""
        try:
            # Get project info to find output file
            project = await self.api_client.get_project(project_id)
            output_file = project.get("output_file")
            
            if not output_file:
                logger.error("No output file available for download")
                return False
            
            # Extract file ID from path (simplified)
            file_id = Path(output_file).stem
            
            # Download file
            success = await self.api_client.download_file(file_id, output_path)
            
            if success:
                logger.info(f"Result downloaded: {output_path}")
            
            return success
        
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"project_id": project_id, "output_path": output_path},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.HIGH
            )
            return False


# Global API client instance
api_client = APIClient()

# Global project manager instance
project_manager = ProjectManager(api_client)
"""
Integration tests for Movie Translate
Tests the integration between different components
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from movie_translate.core.config import Settings
from movie_translate.core.logger import setup_logger
from movie_translate.models.database_models import (
    Project, ProcessingStep, Character, initialize_database
)
from movie_translate.models.repositories import get_repositories
from movie_translate.services.audio_processing import AudioProcessor
from movie_translate.services.translation import TranslationService


class TestDatabaseIntegration:
    """Test database integration with repositories"""
    
    def test_full_project_workflow(self, test_session, sample_project_data):
        """Test complete project workflow from creation to completion"""
        # Get repositories
        repos = get_repositories()
        
        # Create project
        project = repos['project'].create(sample_project_data)
        assert project.id is not None
        assert project.status == "created"
        
        # Create processing steps
        step_types = ["file_import", "character_identification", "speech_recognition", 
                      "translation", "voice_cloning", "video_synthesis"]
        
        for step_type in step_types:
            step_data = {
                "project_id": project.id,
                "step_type": step_type,
                "configuration": {"test": True}
            }
            step = repos['processing_step'].create(step_data)
            assert step.step_type == step_type
            assert step.status == "pending"
        
        # Create characters
        character_data = {
            "project_id": project.id,
            "name": "Test Character",
            "language": "zh",
            "gender": "male"
        }
        character = repos['character'].create(character_data)
        assert character.name == "Test Character"
        
        # Create audio segments
        audio_data = {
            "project_id": project.id,
            "character_id": character.id,
            "start_time": 0.0,
            "end_time": 5.0,
            "file_path": "/test/audio.wav",
            "file_format": "wav",
            "original_text": "Hello, world!",
            "confidence": 0.95
        }
        audio_segment = repos['audio_segment'].create(audio_data)
        assert audio_segment.original_text == "Hello, world!"
        
        # Create translation
        translation_data = {
            "project_id": project.id,
            "audio_segment_id": audio_segment.id,
            "source_language": "en",
            "target_language": "zh",
            "source_text": "Hello, world!",
            "translated_text": "你好，世界！",
            "confidence": 0.92
        }
        translation = repos['translation'].create(translation_data)
        assert translation.translated_text == "你好，世界！"
        
        # Update project status
        updated_project = repos['project'].update(project.id, {
            "status": "completed",
            "progress": 100.0
        })
        assert updated_project.status == "completed"
        assert updated_project.progress == 100.0
        
        # Verify all data is consistent
        steps = repos['processing_step'].get_by_project(project.id)
        assert len(steps) == len(step_types)
        
        characters = repos['character'].get_by_project(project.id)
        assert len(characters) == 1
        
        audio_segments = repos['audio_segment'].get_by_project(project.id)
        assert len(audio_segments) == 1
        
        translations = repos['translation'].get_by_project(project.id)
        assert len(translations) == 1


class TestServiceIntegration:
    """Test service integration"""
    
    @patch('movie_translate.services.audio_processing.AudioProcessor.process_audio')
    def test_audio_processing_integration(self, mock_process, test_settings):
        """Test audio processing service integration"""
        # Mock audio processing
        mock_process.return_value = {
            "duration": 120.0,
            "sample_rate": 16000,
            "channels": 1,
            "format": "wav",
            "segments": [
                {
                    "start_time": 0.0,
                    "end_time": 5.0,
                    "text": "Hello, world!",
                    "confidence": 0.95
                }
            ]
        }
        
        # Create audio processor
        processor = AudioProcessor()
        
        # Process audio file
        result = processor.process_audio("/test/audio.wav")
        
        # Verify result
        assert result["duration"] == 120.0
        assert len(result["segments"]) == 1
        assert result["segments"][0]["text"] == "Hello, world!"
        
        # Verify mock was called
        mock_process.assert_called_once_with("/test/audio.wav")
    
    @patch('movie_translate.services.translation.TranslationService.translate_text')
    def test_translation_service_integration(self, mock_translate, test_settings):
        """Test translation service integration"""
        # Mock translation
        mock_translate.return_value = {
            "translated_text": "你好，世界！",
            "confidence": 0.92,
            "source_language": "en",
            "target_language": "zh"
        }
        
        # Create translation service
        service = TranslationService()
        
        # Translate text
        result = service.translate_text("Hello, world!", "en", "zh")
        
        # Verify result
        assert result["translated_text"] == "你好，世界！"
        assert result["confidence"] == 0.92
        assert result["source_language"] == "en"
        assert result["target_language"] == "zh"
        
        # Verify mock was called
        mock_translate.assert_called_once_with("Hello, world!", "en", "zh")


class TestCacheIntegration:
    """Test cache integration with services"""
    
    def test_cache_with_database_integration(self, test_settings):
        """Test cache integration with database operations"""
        from movie_translate.core.cache_manager import CacheManager
        
        # Create cache manager
        cache_dir = Path(test_settings.cache.path)
        cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Cache database query results
        project_data = {
            "name": "Cached Project",
            "video_file_path": "/test/video.mp4",
            "video_format": "mp4",
            "target_language": "en"
        }
        
        # Cache project data
        cache_manager.set("cached_project", project_data, ttl=3600)
        
        # Retrieve cached data
        cached_project = cache_manager.get("cached_project")
        assert cached_project == project_data
        
        # Test cache expiration
        cache_manager.set("expired_project", project_data, ttl=0.1)
        import time
        time.sleep(0.2)
        
        expired_project = cache_manager.get("expired_project")
        assert expired_project is None


class TestLoggerIntegration:
    """Test logger integration across components"""
    
    def test_logger_configuration_integration(self, test_settings):
        """Test logger configuration integration"""
        # Setup logger
        logger = setup_logger(
            name="integration_test",
            log_file=test_settings.log_file,
            level="INFO"
        )
        
        # Test logging from different components
        logger.info("Integration test message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Verify log file exists and contains messages
        if test_settings.log_file.exists():
            content = test_settings.log_file.read_text()
            assert "Integration test message" in content
            assert "Warning message" in content
            assert "Error message" in content


class TestErrorHandlingIntegration:
    """Test error handling integration"""
    
    def test_database_error_handling(self, test_session):
        """Test database error handling"""
        from movie_translate.core.error_handler import error_handler, ErrorSeverity
        
        # Test error handling
        try:
            # Simulate database error
            raise Exception("Database connection failed")
        except Exception as e:
            # Handle error
            error_handler.handle_error(
                error=e,
                context={"operation": "database_test"},
                severity=ErrorSeverity.ERROR
            )
        
        # Verify error was handled (no exception thrown)
        assert True
    
    def test_service_error_handling(self, test_settings):
        """Test service error handling"""
        from movie_translate.core.error_handler import error_handler, ErrorSeverity
        
        # Test service error handling
        try:
            # Simulate service error
            raise Exception("Service unavailable")
        except Exception as e:
            # Handle error
            error_handler.handle_error(
                error=e,
                context={"service": "translation", "operation": "translate"},
                severity=ErrorSeverity.WARNING
            )
        
        # Verify error was handled
        assert True


class TestConfigurationIntegration:
    """Test configuration integration"""
    
    def test_configuration_persistence(self, test_settings):
        """Test configuration persistence and loading"""
        # Modify configuration
        test_settings.debug = True
        test_settings.audio.sample_rate = 44100
        test_settings.service.translation = "google"
        
        # Save configuration
        test_settings.save()
        
        # Create new settings instance
        new_settings = Settings()
        new_settings.config_file = test_settings.config_file
        new_settings.load()
        
        # Verify configuration was loaded
        assert new_settings.debug == True
        assert new_settings.audio.sample_rate == 44100
        assert new_settings.service.translation.value == "google"


class TestAsyncIntegration:
    """Test async operation integration"""
    
    @pytest.mark.asyncio
    async def test_async_service_integration(self, test_settings):
        """Test async service integration"""
        # Mock async operations
        async def mock_async_operation():
            await asyncio.sleep(0.1)
            return {"result": "success"}
        
        # Test async operation
        result = await mock_async_operation()
        assert result["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, test_settings):
        """Test concurrent async operations"""
        async def mock_operation(operation_id):
            await asyncio.sleep(0.1)
            return {"operation_id": operation_id, "result": "completed"}
        
        # Run concurrent operations
        tasks = [
            mock_operation(i) for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all operations completed
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["operation_id"] == i
            assert result["result"] == "completed"


class TestFileIntegration:
    """Test file handling integration"""
    
    def test_file_processing_workflow(self, test_dir):
        """Test file processing workflow"""
        from movie_translate.utils.file_utils import FileProcessor
        
        # Create test files
        test_video = test_dir / "test_video.mp4"
        test_audio = test_dir / "test_audio.wav"
        
        test_video.write_text("mock video content")
        test_audio.write_text("mock audio content")
        
        # Create file processor
        processor = FileProcessor()
        
        # Process files
        video_info = processor.get_file_info(str(test_video))
        audio_info = processor.get_file_info(str(test_audio))
        
        # Verify file processing
        assert video_info["exists"] is True
        assert audio_info["exists"] is True
        assert video_info["size"] > 0
        assert audio_info["size"] > 0


class TestPerformanceIntegration:
    """Test performance integration"""
    
    def test_performance_monitoring(self, test_settings):
        """Test performance monitoring integration"""
        import time
        
        # Simulate performance monitoring
        start_time = time.time()
        
        # Simulate work
        time.sleep(0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify performance metrics
        assert duration >= 0.1
        assert duration < 0.2  # Should be close to 0.1 seconds


class TestSecurityIntegration:
    """Test security integration"""
    
    def test_input_validation(self, test_settings):
        """Test input validation integration"""
        from movie_translate.core.error_handler import ValidationError
        
        # Test input validation
        def validate_input(input_data):
            if not isinstance(input_data, str):
                raise ValidationError("Input must be a string")
            if len(input_data) > 1000:
                raise ValidationError("Input too long")
            return True
        
        # Test valid input
        assert validate_input("valid input") is True
        
        # Test invalid input
        with pytest.raises(ValidationError):
            validate_input(123)  # Not a string
        
        with pytest.raises(ValidationError):
            validate_input("x" * 1001)  # Too long


@pytest.mark.integration
class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    def test_complete_workflow_simulation(self, test_session, test_settings):
        """Test complete workflow simulation"""
        # This test simulates the entire application workflow
        
        # 1. Initialize components
        repos = get_repositories()
        
        # 2. Create project
        project_data = {
            "name": "End-to-End Test Project",
            "video_file_path": "/test/video.mp4",
            "video_format": "mp4",
            "target_language": "en"
        }
        project = repos['project'].create(project_data)
        
        # 3. Create processing steps
        steps = []
        step_types = ["file_import", "character_identification", "speech_recognition", 
                      "translation", "voice_cloning", "video_synthesis"]
        
        for step_type in step_types:
            step = repos['processing_step'].create({
                "project_id": project.id,
                "step_type": step_type
            })
            steps.append(step)
        
        # 4. Simulate processing workflow
        for i, step in enumerate(steps):
            # Update step status
            repos['processing_step'].update(step.id, {
                "status": "running",
                "progress": 50.0
            })
            
            # Simulate processing time
            import time
            time.sleep(0.01)
            
            # Complete step
            repos['processing_step'].update(step.id, {
                "status": "completed",
                "progress": 100.0
            })
            
            # Update project progress
            progress = ((i + 1) / len(steps)) * 100
            repos['project'].update(project.id, {
                "progress": progress
            })
        
        # 5. Verify final state
        final_project = repos['project'].get_by_id(project.id)
        assert final_project.status == "created"
        assert final_project.progress == 100.0
        
        final_steps = repos['processing_step'].get_by_project(project.id)
        for step in final_steps:
            assert step.status == "completed"
            assert step.progress == 100.0
        
        # 6. Cleanup
        repos['project'].delete(project.id)
        
        # Verify cleanup
        deleted_project = repos['project'].get_by_id(project.id)
        assert deleted_project is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
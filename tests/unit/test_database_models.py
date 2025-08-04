"""
Unit tests for database models
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import inspect

from movie_translate.models.database_models import (
    Project, ProcessingStep, Character, AudioSegment,
    TranslationResult, VoiceCloneModel, ProjectStatus,
    ProcessingStepStatus, Language, VideoFormat,
    DatabaseManager, db_manager
)
from movie_translate.models.schemas import (
    ProjectCreate, CharacterCreate, AudioSegmentCreate,
    TranslationResultCreate, VoiceCloneModelCreate
)


class TestProjectModel:
    """Test Project model"""
    
    def test_project_creation(self, test_session):
        """Test creating a project"""
        project = Project(
            name="Test Project",
            video_file_path="/path/to/video.mp4",
            video_format="mp4",
            target_language="en"
        )
        
        test_session.add(project)
        test_session.commit()
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.status == ProjectStatus.CREATED
        assert project.progress == 0.0
        assert isinstance(project.created_at, datetime)
    
    def test_project_to_dict(self, test_session):
        """Test project to_dict method"""
        project = Project(
            name="Test Project",
            video_file_path="/path/to/video.mp4",
            video_format="mp4",
            target_language="en"
        )
        
        test_session.add(project)
        test_session.commit()
        
        project_dict = project.to_dict()
        
        assert isinstance(project_dict, dict)
        assert project_dict["name"] == "Test Project"
        assert project_dict["status"] == ProjectStatus.CREATED
        assert project_dict["progress"] == 0.0
        assert "id" in project_dict
        assert "created_at" in project_dict
    
    def test_project_relationships(self, test_session, sample_project_data):
        """Test project relationships"""
        # Create project
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create related entities
        character = Character(
            project_id=project.id,
            name="Test Character",
            language="zh"
        )
        
        step = ProcessingStep(
            project_id=project.id,
            step_type="file_import",
            status=ProcessingStepStatus.PENDING
        )
        
        test_session.add(character)
        test_session.add(step)
        test_session.commit()
        
        # Test relationships
        assert len(project.characters) == 1
        assert len(project.processing_steps) == 1
        assert project.characters[0].name == "Test Character"
        assert project.processing_steps[0].step_type == "file_import"


class TestProcessingStepModel:
    """Test ProcessingStep model"""
    
    def test_processing_step_creation(self, test_session, sample_project_data):
        """Test creating a processing step"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create processing step
        step = ProcessingStep(
            project_id=project.id,
            step_type="file_import",
            configuration={"param1": "value1"}
        )
        
        test_session.add(step)
        test_session.commit()
        
        assert step.id is not None
        assert step.project_id == project.id
        assert step.step_type == "file_import"
        assert step.status == ProcessingStepStatus.PENDING
        assert step.progress == 0.0
        assert step.configuration == {"param1": "value1"}
    
    def test_processing_step_to_dict(self, test_session, sample_project_data):
        """Test processing step to_dict method"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create processing step
        step = ProcessingStep(
            project_id=project.id,
            step_type="file_import"
        )
        
        test_session.add(step)
        test_session.commit()
        
        step_dict = step.to_dict()
        
        assert isinstance(step_dict, dict)
        assert step_dict["project_id"] == project.id
        assert step_dict["step_type"] == "file_import"
        assert step_dict["status"] == ProcessingStepStatus.PENDING
        assert "id" in step_dict


class TestCharacterModel:
    """Test Character model"""
    
    def test_character_creation(self, test_session, sample_project_data):
        """Test creating a character"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create character
        character = Character(
            project_id=project.id,
            name="Test Character",
            language="zh",
            gender="male",
            age_group="adult"
        )
        
        test_session.add(character)
        test_session.commit()
        
        assert character.id is not None
        assert character.project_id == project.id
        assert character.name == "Test Character"
        assert character.language == "zh"
        assert character.sample_count == 0
        assert character.total_duration == 0.0
    
    def test_character_to_dict(self, test_session, sample_project_data):
        """Test character to_dict method"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create character
        character = Character(
            project_id=project.id,
            name="Test Character",
            language="zh"
        )
        
        test_session.add(character)
        test_session.commit()
        
        character_dict = character.to_dict()
        
        assert isinstance(character_dict, dict)
        assert character_dict["project_id"] == project.id
        assert character_dict["name"] == "Test Character"
        assert character_dict["language"] == "zh"
        assert "id" in character_dict


class TestAudioSegmentModel:
    """Test AudioSegment model"""
    
    def test_audio_segment_creation(self, test_session, sample_project_data):
        """Test creating an audio segment"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create audio segment
        segment = AudioSegment(
            project_id=project.id,
            start_time=0.0,
            end_time=5.0,
            file_path="/path/to/audio.wav",
            file_format="wav",
            original_text="Hello, world!",
            confidence=0.95
        )
        
        test_session.add(segment)
        test_session.commit()
        
        assert segment.id is not None
        assert segment.project_id == project.id
        assert segment.start_time == 0.0
        assert segment.end_time == 5.0
        assert segment.duration == 5.0
        assert segment.original_text == "Hello, world!"
        assert segment.confidence == 0.95
        assert segment.processed is False
    
    def test_audio_segment_to_dict(self, test_session, sample_project_data):
        """Test audio segment to_dict method"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create audio segment
        segment = AudioSegment(
            project_id=project.id,
            start_time=0.0,
            end_time=5.0,
            file_path="/path/to/audio.wav",
            file_format="wav"
        )
        
        test_session.add(segment)
        test_session.commit()
        
        segment_dict = segment.to_dict()
        
        assert isinstance(segment_dict, dict)
        assert segment_dict["project_id"] == project.id
        assert segment_dict["start_time"] == 0.0
        assert segment_dict["end_time"] == 5.0
        assert segment_dict["duration"] == 5.0
        assert "id" in segment_dict


class TestTranslationResultModel:
    """Test TranslationResult model"""
    
    def test_translation_result_creation(self, test_session, sample_project_data):
        """Test creating a translation result"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create translation result
        translation = TranslationResult(
            project_id=project.id,
            source_language="en",
            target_language="zh",
            source_text="Hello, world!",
            translated_text="你好，世界！",
            confidence=0.92,
            translation_service="google"
        )
        
        test_session.add(translation)
        test_session.commit()
        
        assert translation.id is not None
        assert translation.project_id == project.id
        assert translation.source_language == "en"
        assert translation.target_language == "zh"
        assert translation.source_text == "Hello, world!"
        assert translation.translated_text == "你好，世界！"
        assert translation.confidence == 0.92
    
    def test_translation_result_to_dict(self, test_session, sample_project_data):
        """Test translation result to_dict method"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create translation result
        translation = TranslationResult(
            project_id=project.id,
            source_language="en",
            target_language="zh",
            source_text="Hello, world!",
            translated_text="你好，世界！"
        )
        
        test_session.add(translation)
        test_session.commit()
        
        translation_dict = translation.to_dict()
        
        assert isinstance(translation_dict, dict)
        assert translation_dict["project_id"] == project.id
        assert translation_dict["source_language"] == "en"
        assert translation_dict["target_language"] == "zh"
        assert translation_dict["source_text"] == "Hello, world!"
        assert translation_dict["translated_text"] == "你好，世界！"
        assert "id" in translation_dict


class TestVoiceCloneModelModel:
    """Test VoiceCloneModel model"""
    
    def test_voice_clone_model_creation(self, test_session, sample_project_data):
        """Test creating a voice clone model"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create voice clone model
        model = VoiceCloneModel(
            project_id=project.id,
            model_name="Test Model",
            model_type="f5-tts",
            model_version="1.0",
            training_samples=100,
            training_epochs=10,
            training_loss=0.05
        )
        
        test_session.add(model)
        test_session.commit()
        
        assert model.id is not None
        assert model.project_id == project.id
        assert model.model_name == "Test Model"
        assert model.model_type == "f5-tts"
        assert model.model_version == "1.0"
        assert model.training_samples == 100
        assert model.training_epochs == 10
        assert model.training_loss == 0.05
        assert model.status == "training"
    
    def test_voice_clone_model_to_dict(self, test_session, sample_project_data):
        """Test voice clone model to_dict method"""
        # Create project first
        project = Project(**sample_project_data)
        test_session.add(project)
        test_session.commit()
        
        # Create voice clone model
        model = VoiceCloneModel(
            project_id=project.id,
            model_name="Test Model",
            model_type="f5-tts"
        )
        
        test_session.add(model)
        test_session.commit()
        
        model_dict = model.to_dict()
        
        assert isinstance(model_dict, dict)
        assert model_dict["project_id"] == project.id
        assert model_dict["model_name"] == "Test Model"
        assert model_dict["model_type"] == "f5-tts"
        assert "id" in model_dict


class TestDatabaseManager:
    """Test DatabaseManager class"""
    
    def test_database_manager_initialization(self, test_settings):
        """Test database manager initialization"""
        manager = DatabaseManager()
        
        assert manager.engine is None
        assert manager.SessionLocal is None
        assert manager.session is None
    
    def test_initialize_database(self, test_settings):
        """Test database initialization"""
        manager = DatabaseManager()
        manager.initialize()
        
        assert manager.engine is not None
        assert manager.SessionLocal is not None
        
        # Check that tables were created
        inspector = inspect(manager.engine)
        table_names = inspector.get_table_names()
        
        expected_tables = [
            "projects", "processing_steps", "characters",
            "audio_segments", "translation_results", "voice_clone_models"
        ]
        
        for table in expected_tables:
            assert table in table_names
    
    def test_get_session(self, test_settings):
        """Test getting database session"""
        manager = DatabaseManager()
        manager.initialize()
        
        session = manager.get_session()
        
        assert session is not None
        assert session is manager.session
    
    def test_close_session(self, test_settings):
        """Test closing database session"""
        manager = DatabaseManager()
        manager.initialize()
        
        # Get session
        session = manager.get_session()
        assert manager.session is not None
        
        # Close session
        manager.close_session()
        assert manager.session is None
    
    def test_create_project(self, test_settings, sample_project_data):
        """Test creating project through database manager"""
        manager = DatabaseManager()
        manager.initialize()
        
        project = manager.create_project(sample_project_data)
        
        assert project.id is not None
        assert project.name == sample_project_data["name"]
        assert project.status == ProjectStatus.CREATED
    
    def test_get_project(self, test_settings, sample_project_data):
        """Test getting project through database manager"""
        manager = DatabaseManager()
        manager.initialize()
        
        # Create project
        created_project = manager.create_project(sample_project_data)
        
        # Get project
        retrieved_project = manager.get_project(created_project.id)
        
        assert retrieved_project is not None
        assert retrieved_project.id == created_project.id
        assert retrieved_project.name == created_project.name
    
    def test_update_project(self, test_settings, sample_project_data):
        """Test updating project through database manager"""
        manager = DatabaseManager()
        manager.initialize()
        
        # Create project
        project = manager.create_project(sample_project_data)
        
        # Update project
        update_data = {"name": "Updated Project", "progress": 50.0}
        updated_project = manager.update_project(project.id, update_data)
        
        assert updated_project is not None
        assert updated_project.name == "Updated Project"
        assert updated_project.progress == 50.0
    
    def test_delete_project(self, test_settings, sample_project_data):
        """Test deleting project through database manager"""
        manager = DatabaseManager()
        manager.initialize()
        
        # Create project
        project = manager.create_project(sample_project_data)
        project_id = project.id
        
        # Delete project
        result = manager.delete_project(project_id)
        assert result is True
        
        # Verify project is gone
        deleted_project = manager.get_project(project_id)
        assert deleted_project is None
    
    def test_list_projects(self, test_settings, sample_project_data):
        """Test listing projects through database manager"""
        manager = DatabaseManager()
        manager.initialize()
        
        # Create multiple projects
        project1 = manager.create_project(sample_project_data)
        project2_data = sample_project_data.copy()
        project2_data["name"] = "Project 2"
        project2 = manager.create_project(project2_data)
        
        # List projects
        projects = manager.list_projects()
        
        assert len(projects) >= 2
        project_names = [p.name for p in projects]
        assert project1.name in project_names
        assert project2.name in project_names
    
    def test_create_processing_step(self, test_settings, sample_project_data):
        """Test creating processing step through database manager"""
        manager = DatabaseManager()
        manager.initialize()
        
        # Create project first
        project = manager.create_project(sample_project_data)
        
        # Create processing step
        step_data = {
            "project_id": project.id,
            "step_type": "file_import",
            "configuration": {"param": "value"}
        }
        step = manager.create_processing_step(step_data)
        
        assert step.id is not None
        assert step.project_id == project.id
        assert step.step_type == "file_import"
    
    def test_get_processing_steps(self, test_settings, sample_project_data):
        """Test getting processing steps through database manager"""
        manager = DatabaseManager()
        manager.initialize()
        
        # Create project first
        project = manager.create_project(sample_project_data)
        
        # Create processing steps
        step1_data = {"project_id": project.id, "step_type": "file_import"}
        step2_data = {"project_id": project.id, "step_type": "character_identification"}
        step1 = manager.create_processing_step(step1_data)
        step2 = manager.create_processing_step(step2_data)
        
        # Get processing steps
        steps = manager.get_processing_steps(project.id)
        
        assert len(steps) == 2
        step_types = [s.step_type for s in steps]
        assert "file_import" in step_types
        assert "character_identification" in step_types


if __name__ == "__main__":
    pytest.main([__file__])
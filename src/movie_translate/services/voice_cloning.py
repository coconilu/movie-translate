"""
Voice cloning service for Movie Translate
"""

import asyncio
import numpy as np
import librosa
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import tempfile
import json

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity, cache_manager
from ..utils.audio_utils import AudioUtils
from .audio_processing import AudioSegment, AudioAnalysisResult
from .character_identification import VoiceProfile, CharacterIdentificationService


@dataclass
class VoiceCloningResult:
    """Voice cloning result"""
    character_id: str
    text: str
    audio_path: str
    duration: float
    sample_rate: int
    confidence: float
    service_used: str
    generation_time: float
    audio_quality: Dict[str, float] = None


@dataclass
class VoiceModel:
    """Voice model for cloning"""
    character_id: str
    model_type: str  # "f5_tts" or "minimax"
    model_path: str
    training_data: List[str]
    created_at: datetime
    last_used: datetime
    performance_metrics: Dict[str, float] = None


class F5TTSService:
    """F5-TTS voice cloning service"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.model_dir = settings.get_cache_path() / "f5_tts_models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
    async def clone_voice(self, text: str, voice_profile: VoiceProfile, 
                         output_path: str) -> VoiceCloningResult:
        """Clone voice using F5-TTS"""
        try:
            # Check cache first
            cache_key = f"f5_tts_{hash(text)}_{voice_profile.character_id}"
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Using cached F5-TTS result")
                return VoiceCloningResult(**cached_result)
            
            # Load model if not loaded
            if not self.model_loaded:
                await self._load_model()
            
            # Prepare text
            processed_text = self._preprocess_text(text)
            
            # Generate audio
            start_time = datetime.now()
            audio_data, sample_rate = await self._generate_audio(processed_text, voice_profile)
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Save audio
            AudioUtils.save_audio_segment(audio_data, output_path)
            
            # Analyze audio quality
            audio_quality = await self._analyze_audio_quality(audio_data, sample_rate)
            
            # Create result
            result = VoiceCloningResult(
                character_id=voice_profile.character_id,
                text=text,
                audio_path=output_path,
                duration=len(audio_data) / sample_rate,
                sample_rate=sample_rate,
                confidence=0.9,  # F5-TTS typically has high confidence
                service_used="f5_tts",
                generation_time=generation_time,
                audio_quality=audio_quality
            )
            
            # Cache result
            cache_manager.put(cache_key, result.__dict__, ttl=3600)
            
            logger.info(f"F5-TTS voice cloning completed: {text[:30]}...")
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"service": "f5_tts", "character_id": voice_profile.character_id},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _load_model(self):
        """Load F5-TTS model"""
        try:
            logger.info("Loading F5-TTS model...")
            
            # This is a placeholder for actual F5-TTS model loading
            # In practice, you would load the actual model here
            
            # Simulate model loading
            await asyncio.sleep(2)
            
            self.model_loaded = True
            logger.info("F5-TTS model loaded successfully")
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "load_f5_tts_model"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for TTS"""
        try:
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            # Add punctuation if missing
            if not text.endswith(('.', '!', '?', '。', '！', '？')):
                text += '。'
            
            return text
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "preprocess_text"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.LOW
            )
            return text
    
    async def _generate_audio(self, text: str, voice_profile: VoiceProfile) -> Tuple[np.ndarray, int]:
        """Generate audio using F5-TTS"""
        try:
            # This is a placeholder for actual F5-TTS audio generation
            # In practice, you would use the loaded model here
            
            # Simulate audio generation
            await asyncio.sleep(1)
            
            # Generate mock audio data
            duration = len(text) * 0.1  # Rough estimate
            sample_rate = 22050
            t = np.linspace(0, duration, int(duration * sample_rate))
            
            # Generate synthetic audio with voice profile characteristics
            frequency = 220 + np.mean(voice_profile.voice_features[:5]) * 100
            audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
            
            # Add some harmonics for more natural sound
            for harmonic in range(2, 5):
                audio_data += np.sin(2 * np.pi * frequency * harmonic * t) * (0.3 / harmonic)
            
            # Apply envelope
            envelope = np.exp(-t / (duration * 0.3))
            audio_data *= envelope
            
            # Add some noise for naturalness
            noise = np.random.normal(0, 0.01, len(audio_data))
            audio_data += noise
            
            return audio_data, sample_rate
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "generate_audio"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _analyze_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze generated audio quality"""
        try:
            quality_metrics = {}
            
            # Calculate SNR
            signal_power = np.mean(audio_data ** 2)
            noise_power = np.var(audio_data)
            snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 60
            quality_metrics['snr_db'] = snr
            
            # Calculate spectral characteristics
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            quality_metrics['spectral_centroid'] = float(np.mean(spectral_centroids))
            
            # Calculate MFCC consistency
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            quality_metrics['mfcc_consistency'] = float(np.std(mfccs))
            
            # Calculate zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y=audio_data)
            quality_metrics['zero_crossing_rate'] = float(np.mean(zcr))
            
            return quality_metrics
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "analyze_audio_quality"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return {}


class MiniMaxService:
    """MiniMax voice cloning service"""
    
    def __init__(self):
        self.api_key = settings.get_api_key("minimax_api_key")
        self.base_url = "https://api.minimax.chat/v1"
        self.model_id = settings.voice_cloning.minimax_model_id
        
    async def clone_voice(self, text: str, voice_profile: VoiceProfile, 
                         output_path: str) -> VoiceCloningResult:
        """Clone voice using MiniMax API"""
        try:
            # Check cache first
            cache_key = f"minimax_{hash(text)}_{voice_profile.character_id}"
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Using cached MiniMax result")
                return VoiceCloningResult(**cached_result)
            
            # Prepare voice reference
            voice_reference = await self._prepare_voice_reference(voice_profile)
            
            # Generate audio
            start_time = datetime.now()
            audio_data = await self._generate_audio(text, voice_reference)
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Save audio
            AudioUtils.save_audio_segment(audio_data, output_path)
            
            # Analyze audio quality
            audio_quality = await self._analyze_audio_quality(audio_data, voice_profile.sample_rate)
            
            # Create result
            result = VoiceCloningResult(
                character_id=voice_profile.character_id,
                text=text,
                audio_path=output_path,
                duration=len(audio_data) / voice_profile.sample_rate,
                sample_rate=voice_profile.sample_rate,
                confidence=0.85,  # MiniMax typically has good confidence
                service_used="minimax",
                generation_time=generation_time,
                audio_quality=audio_quality
            )
            
            # Cache result
            cache_manager.put(cache_key, result.__dict__, ttl=3600)
            
            logger.info(f"MiniMax voice cloning completed: {text[:30]}...")
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"service": "minimax", "character_id": voice_profile.character_id},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _prepare_voice_reference(self, voice_profile: VoiceProfile) -> Dict[str, Any]:
        """Prepare voice reference for MiniMax"""
        try:
            # Convert voice features to compatible format
            reference = {
                'voice_features': voice_profile.voice_features.tolist(),
                'sample_rate': voice_profile.sample_rate,
                'character_name': voice_profile.character_name,
                'language': voice_profile.language
            }
            
            return reference
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"character_id": voice_profile.character_id},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            raise
    
    async def _generate_audio(self, text: str, voice_reference: Dict[str, Any]) -> np.ndarray:
        """Generate audio using MiniMax API"""
        try:
            import requests
            
            url = f"{self.base_url}/tts"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_id,
                "text": text,
                "voice_reference": voice_reference,
                "language": voice_reference['language'],
                "speed": 1.0,
                "pitch": 0.0,
                "volume": 1.0
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result_data = response.json()
            
            if "error" in result_data:
                raise RuntimeError(f"MiniMax API error: {result_data['error']}")
            
            # Convert response to audio data
            audio_data = self._convert_response_to_audio(result_data)
            
            return audio_data
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "generate_audio"},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _convert_response_to_audio(self, response_data: Dict[str, Any]) -> np.ndarray:
        """Convert API response to audio data"""
        try:
            # This is a placeholder for actual audio conversion
            # In practice, you would decode the audio data from the API response
            
            # Generate mock audio data for demonstration
            duration = len(response_data.get('text', '')) * 0.1
            sample_rate = 22050
            t = np.linspace(0, duration, int(duration * sample_rate))
            
            # Generate synthetic audio
            frequency = 200 + np.random.random() * 100
            audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
            
            return audio_data
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "convert_response_to_audio"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _analyze_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Analyze generated audio quality"""
        try:
            quality_metrics = {}
            
            # Calculate basic metrics
            quality_metrics['rms_energy'] = float(np.sqrt(np.mean(audio_data ** 2)))
            quality_metrics['peak_amplitude'] = float(np.max(np.abs(audio_data)))
            
            # Calculate spectral characteristics
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            quality_metrics['spectral_centroid'] = float(np.mean(spectral_centroids))
            
            return quality_metrics
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "analyze_audio_quality"},
                category=ErrorCategory.PROCESSING,
                Severity=ErrorSeverity.MEDIUM
            )
            return {}


class VoiceCloningService:
    """Main voice cloning service"""
    
    def __init__(self):
        self.f5_tts_service = F5TTSService()
        self.minimax_service = MiniMaxService()
        self.character_service = CharacterIdentificationService()
        self.primary_service = settings.voice_cloning.primary_service
        
        # Voice model storage
        self.voice_models: Dict[str, VoiceModel] = {}
        self.model_dir = settings.get_cache_path() / "voice_models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing voice models
        self._load_voice_models()
    
    async def clone_voice_for_character(self, character_id: str, text: str, 
                                      output_path: str) -> VoiceCloningResult:
        """Clone voice for specific character"""
        try:
            # Get voice profile
            voice_profile = self.character_service.voice_profiles.get(character_id)
            if not voice_profile:
                raise ValueError(f"Voice profile not found for character: {character_id}")
            
            # Use primary service
            if self.primary_service == "f5_tts":
                result = await self.f5_tts_service.clone_voice(text, voice_profile, output_path)
            elif self.primary_service == "minimax":
                result = await self.minimax_service.clone_voice(text, voice_profile, output_path)
            else:
                raise ValueError(f"Unsupported primary service: {self.primary_service}")
            
            # Update voice model usage
            await self._update_voice_model_usage(character_id)
            
            logger.info(f"Voice cloning completed for {character_id}: {text[:30]}...")
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"character_id": character_id, "text": text[:50]},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def clone_all_segments(self, audio_analysis: AudioAnalysisResult, 
                                output_dir: str) -> List[VoiceCloningResult]:
        """Clone voice for all audio segments"""
        try:
            logger.info(f"Starting voice cloning for {len(audio_analysis.segments)} segments")
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Group segments by character
            character_segments = self._group_segments_by_character(audio_analysis.segments)
            
            # Clone voice for each character
            all_results = []
            
            for character_id, segments in character_segments.items():
                logger.info(f"Cloning voice for character: {character_id} ({len(segments)} segments)")
                
                # Process segments in batches
                batch_size = settings.voice_cloning.batch_size
                
                for i in range(0, len(segments), batch_size):
                    batch = segments[i:i + batch_size]
                    
                    # Process batch asynchronously
                    tasks = []
                    for segment in batch:
                        if segment.text:
                            output_path = output_dir / f"{segment.id}_cloned.wav"
                            task = self.clone_voice_for_character(
                                character_id, segment.text, str(output_path)
                            )
                            tasks.append(task)
                    
                    if tasks:
                        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        # Handle results
                        for result in batch_results:
                            if isinstance(result, Exception):
                                logger.error(f"Voice cloning error: {result}")
                            else:
                                all_results.append(result)
                    
                    # Update progress
                    progress = min((i + len(batch)) / len(segments), 1.0)
                    logger.info(f"Voice cloning progress: {progress:.2%}")
            
            logger.info("Voice cloning completed for all segments")
            return all_results
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"output_dir": output_dir, "segment_count": len(audio_analysis.segments)},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _group_segments_by_character(self, segments: List[AudioSegment]) -> Dict[str, List[AudioSegment]]:
        """Group segments by character"""
        groups = {}
        for segment in segments:
            character_id = segment.speaker_id or "unknown"
            if character_id not in groups:
                groups[character_id] = []
            groups[character_id].append(segment)
        return groups
    
    async def _update_voice_model_usage(self, character_id: str):
        """Update voice model usage timestamp"""
        try:
            if character_id in self.voice_models:
                self.voice_models[character_id].last_used = datetime.now()
                # Save updated model info
                await self._save_voice_model(self.voice_models[character_id])
                
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"character_id": character_id},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.LOW
            )
    
    async def _save_voice_model(self, model: VoiceModel):
        """Save voice model information"""
        try:
            model_path = self.model_dir / f"{model.character_id}.json"
            
            model_data = {
                'character_id': model.character_id,
                'model_type': model.model_type,
                'model_path': model.model_path,
                'training_data': model.training_data,
                'created_at': model.created_at.isoformat(),
                'last_used': model.last_used.isoformat(),
                'performance_metrics': model.performance_metrics
            }
            
            with open(model_path, 'w', encoding='utf-8') as f:
                json.dump(model_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"character_id": model.character_id},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
    
    def _load_voice_models(self):
        """Load voice models from disk"""
        try:
            for model_file in self.model_dir.glob("*.json"):
                try:
                    with open(model_file, 'r', encoding='utf-8') as f:
                        model_data = json.load(f)
                    
                    model = VoiceModel(
                        character_id=model_data['character_id'],
                        model_type=model_data['model_type'],
                        model_path=model_data['model_path'],
                        training_data=model_data['training_data'],
                        created_at=datetime.fromisoformat(model_data['created_at']),
                        last_used=datetime.fromisoformat(model_data['last_used']),
                        performance_metrics=model_data.get('performance_metrics')
                    )
                    
                    self.voice_models[model.character_id] = model
                    
                except Exception as e:
                    logger.warning(f"Failed to load voice model {model_file}: {e}")
                    continue
            
            logger.info(f"Loaded {len(self.voice_models)} voice models")
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "load_voice_models"},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
    
    async def create_voice_model(self, character_id: str, model_type: str, 
                               training_data: List[str]) -> bool:
        """Create new voice model for character"""
        try:
            # Get voice profile
            voice_profile = self.character_service.voice_profiles.get(character_id)
            if not voice_profile:
                raise ValueError(f"Voice profile not found for character: {character_id}")
            
            # Create model
            model_path = self.model_dir / f"{character_id}_{model_type}.model"
            
            model = VoiceModel(
                character_id=character_id,
                model_type=model_type,
                model_path=str(model_path),
                training_data=training_data,
                created_at=datetime.now(),
                last_used=datetime.now()
            )
            
            # Save model
            self.voice_models[character_id] = model
            await self._save_voice_model(model)
            
            logger.info(f"Voice model created: {character_id} ({model_type})")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"character_id": character_id, "model_type": model_type},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    async def merge_cloned_audio(self, audio_files: List[str], output_path: str) -> bool:
        """Merge multiple cloned audio files"""
        try:
            # Use audio utils to merge files
            success = AudioUtils.merge_audio_files(audio_files, output_path)
            
            if success:
                logger.info(f"Cloned audio merged: {len(audio_files)} files -> {output_path}")
            
            return success
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"audio_files": audio_files, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False


# Create singleton instance
voice_cloning_service = VoiceCloningService()
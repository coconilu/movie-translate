"""
Speech recognition service for Movie Translate
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import numpy as np
import tempfile
import os
from datetime import datetime

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity, cache_manager
from .audio_processing import AudioSegment, AudioAnalysisResult


class SpeechRecognitionResult:
    """Speech recognition result"""
    
    def __init__(self, segment_id: str, text: str, confidence: float, 
                 language: str = None, alternatives: List[Dict] = None):
        self.segment_id = segment_id
        self.text = text
        self.confidence = confidence
        self.language = language
        self.alternatives = alternatives or []
        self.timestamp = datetime.now()


class BaiduSpeechRecognition:
    """Baidu speech recognition service"""
    
    def __init__(self):
        self.app_id = settings.get_api_key("baidu_app_id")
        self.api_key = settings.get_api_key("baidu_api_key")
        self.secret_key = settings.get_api_key("baidu_secret_key")
        self.access_token = None
        self.token_expires = None
        
    async def _initialize(self):
        """Initialize the service"""
        logger.info("Baidu speech recognition service initialized")
        return True
        
    async def recognize(self, audio_data: np.ndarray, sample_rate: int, 
                       language: str = "zh") -> SpeechRecognitionResult:
        """Recognize speech using Baidu API"""
        try:
            # Check cache first
            cache_key = f"baidu_speech_{hash(audio_data.tobytes())}_{language}"
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Using cached Baidu speech recognition result")
                return SpeechRecognitionResult(**cached_result)
            
            # Get access token
            if not self.access_token or self._is_token_expired():
                await self._refresh_access_token()
            
            # Prepare audio data
            audio_data = self._prepare_audio_data(audio_data, sample_rate)
            
            # Call Baidu API
            result = await self._call_baidu_api(audio_data, language)
            
            # Cache result
            cache_manager.put(cache_key, result.__dict__, ttl=3600)  # 1 hour cache
            
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"service": "baidu_speech", "language": language},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _prepare_audio_data(self, audio_data: np.ndarray, sample_rate: int) -> bytes:
        """Prepare audio data for Baidu API"""
        try:
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                import librosa
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
            
            # Convert to 16-bit PCM
            audio_data = (audio_data * 32767).astype(np.int16)
            
            return audio_data.tobytes()
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "prepare_audio_data"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            raise
    
    async def _refresh_access_token(self):
        """Refresh Baidu API access token"""
        try:
            import requests
            
            url = "https://aip.baidubce.com/oauth/2.0/token"
            params = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.secret_key
            }
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires = datetime.now().timestamp() + data["expires_in"] - 300
            
            logger.info("Baidu access token refreshed successfully")
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "refresh_access_token"},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expires:
            return True
        return datetime.now().timestamp() > self.token_expires
    
    async def _call_baidu_api(self, audio_data: bytes, language: str) -> SpeechRecognitionResult:
        """Call Baidu speech recognition API"""
        try:
            import requests
            
            url = f"https://aip.baidubce.com/server_api/v1/recognize"
            headers = {
                "Content-Type": "audio/pcm;rate=16000",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            params = {
                "dev_pid": 1737 if language == "zh" else 1736,  # Chinese or English
                "cuid": "movie_translate_device",
                "token": self.access_token
            }
            
            response = requests.post(url, headers=headers, params=params, data=audio_data)
            response.raise_for_status()
            
            data = response.json()
            
            if data["err_no"] != 0:
                raise RuntimeError(f"Baidu API error: {data['err_msg']}")
            
            # Parse result
            result = data["result"]
            if not result:
                raise RuntimeError("No recognition result from Baidu")
            
            text = result[0]
            confidence = data.get("confidence", 0.0)
            
            return SpeechRecognitionResult(
                segment_id="baidu_result",
                text=text,
                confidence=confidence,
                language=language
            )
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "call_baidu_api"},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise


class SenseVoiceRecognition:
    """SenseVoice speech recognition service"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        
    async def _initialize(self):
        """Initialize the service"""
        logger.info("SenseVoice speech recognition service initialized")
        return True
        
    async def recognize(self, audio_data: np.ndarray, sample_rate: int, 
                       language: str = "zh") -> SpeechRecognitionResult:
        """Recognize speech using SenseVoice"""
        try:
            # Check cache first
            cache_key = f"sensevoice_{hash(audio_data.tobytes())}_{language}"
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Using cached SenseVoice recognition result")
                return SpeechRecognitionResult(**cached_result)
            
            # Load model if not loaded
            if not self.model_loaded:
                await self._load_model()
            
            # Prepare audio data
            audio_data = self._prepare_audio_data(audio_data, sample_rate)
            
            # Recognize speech
            result = await self._recognize_with_model(audio_data, language)
            
            # Cache result
            cache_manager.put(cache_key, result.__dict__, ttl=3600)
            
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"service": "sensevoice", "language": language},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _load_model(self):
        """Load SenseVoice model"""
        try:
            # This is a placeholder for actual SenseVoice model loading
            # In practice, you would load the actual model here
            
            logger.info("Loading SenseVoice model...")
            
            # Simulate model loading
            await asyncio.sleep(1)
            
            self.model_loaded = True
            logger.info("SenseVoice model loaded successfully")
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "load_sensevoice_model"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _prepare_audio_data(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Prepare audio data for SenseVoice"""
        try:
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                import librosa
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
            
            # Normalize audio
            audio_data = librosa.util.normalize(audio_data)
            
            return audio_data
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "prepare_audio_data"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            raise
    
    async def _recognize_with_model(self, audio_data: np.ndarray, language: str) -> SpeechRecognitionResult:
        """Recognize speech using SenseVoice model"""
        try:
            # This is a placeholder for actual speech recognition
            # In practice, you would use the loaded model here
            
            # Simulate recognition
            await asyncio.sleep(0.5)
            
            # Mock result for demonstration
            text = "这是语音识别的示例文本" if language == "zh" else "This is example speech recognition text"
            confidence = 0.95
            
            return SpeechRecognitionResult(
                segment_id="sensevoice_result",
                text=text,
                confidence=confidence,
                language=language
            )
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "recognize_with_model"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise


class SpeechRecognitionService:
    """Main speech recognition service"""
    
    def __init__(self):
        self.baidu_service = BaiduSpeechRecognition()
        self.sensevoice_service = SenseVoiceRecognition()
        self.primary_service = settings.speech.primary_service
        
    async def _initialize(self):
        """Initialize the service"""
        logger.info("Speech recognition service initialized")
        return True
        
    async def recognize_segment(self, segment: AudioSegment, 
                              language: str = "auto") -> SpeechRecognitionResult:
        """Recognize speech from audio segment"""
        try:
            if segment.audio_data is None:
                raise ValueError("No audio data in segment")
            
            # Detect language if auto
            if language == "auto":
                language = await self._detect_language(segment)
            
            # Use primary service
            if self.primary_service == "baidu":
                result = await self.baidu_service.recognize(
                    segment.audio_data, segment.sample_rate, language
                )
            elif self.primary_service == "sensevoice":
                result = await self.sensevoice_service.recognize(
                    segment.audio_data, segment.sample_rate, language
                )
            else:
                raise ValueError(f"Unsupported primary service: {self.primary_service}")
            
            # Update segment with recognition result
            segment.text = result.text
            segment.language = result.language
            segment.confidence = result.confidence
            
            logger.info(f"Speech recognition completed for segment {segment.id}: {result.text[:50]}...")
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"segment_id": segment.id, "language": language},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def recognize_all_segments(self, audio_analysis: AudioAnalysisResult, 
                                   language: str = "auto") -> AudioAnalysisResult:
        """Recognize speech from all audio segments"""
        try:
            logger.info(f"Starting speech recognition for {len(audio_analysis.segments)} segments")
            
            # Process segments in batches
            processed_segments = []
            batch_size = settings.speech.batch_size
            
            for i in range(0, len(audio_analysis.segments), batch_size):
                batch = audio_analysis.segments[i:i + batch_size]
                
                # Process batch asynchronously
                tasks = []
                for segment in batch:
                    task = self.recognize_segment(segment, language)
                    tasks.append(task)
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle results
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Error recognizing segment {batch[j].id}: {result}")
                        # Keep original segment if recognition fails
                        processed_segments.append(batch[j])
                    else:
                        processed_segments.append(batch[j])
                
                # Update progress
                progress = min((i + len(batch)) / len(audio_analysis.segments), 1.0)
                logger.info(f"Speech recognition progress: {progress:.2%}")
            
            # Update analysis result
            audio_analysis.segments = processed_segments
            
            logger.info("Speech recognition completed for all segments")
            return audio_analysis
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "recognize_all_segments", "segment_count": len(audio_analysis.segments)},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _detect_language(self, segment: AudioSegment) -> str:
        """Detect language from audio segment"""
        try:
            # Use existing language detection from audio analysis
            if segment.language:
                return segment.language
            
            # If no language detected, use default
            return settings.speech.default_language
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"segment_id": segment.id},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return settings.speech.default_language
    
    async def transcribe_to_srt(self, audio_analysis: AudioAnalysisResult, 
                               output_path: str) -> bool:
        """Transcribe audio segments to SRT format"""
        try:
            srt_content = []
            
            for i, segment in enumerate(audio_analysis.segments):
                if not segment.text:
                    continue
                
                # Format time for SRT
                start_time = self._format_srt_time(segment.start_time)
                end_time = self._format_srt_time(segment.end_time)
                
                # Create SRT entry
                srt_entry = f"{i + 1}\n{start_time} --> {end_time}\n{segment.text}\n"
                srt_content.append(srt_entry)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(srt_content))
            
            logger.info(f"SRT file saved to: {output_path}")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"output_path": output_path},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format time in seconds to SRT format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"


# Create singleton instance
speech_recognition_service = SpeechRecognitionService()
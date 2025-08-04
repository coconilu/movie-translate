"""
Audio processing service for Movie Translate
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from dataclasses import dataclass
import tempfile
import os

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity, cache_manager, progress_manager
from ..utils.audio_utils import AudioUtils
from ..utils.file_utils import FileUtils


@dataclass
class AudioSegment:
    """Audio segment data structure"""
    id: str
    start_time: float
    end_time: float
    duration: float
    audio_data: Optional[np.ndarray] = None
    sample_rate: int = 16000
    speaker_id: Optional[str] = None
    text: Optional[str] = None
    language: Optional[str] = None
    confidence: float = 0.0


@dataclass
class AudioAnalysisResult:
    """Audio analysis result"""
    segments: List[AudioSegment]
    total_duration: float
    sample_rate: int
    channels: int
    format: str
    speakers: List[str]
    language: Optional[str] = None
    audio_quality: Dict[str, float] = None


class AudioProcessingService:
    """Audio processing service for movie translation"""
    
    def __init__(self):
        self.sample_rate = settings.audio.sample_rate
        self.channels = settings.audio.channels
        self.chunk_size = settings.audio.chunk_size
        self.temp_dir = settings.get_temp_path()
        
    async def process_video_audio(self, video_path: str) -> AudioAnalysisResult:
        """Process audio from video file"""
        try:
            logger.info(f"Processing audio from video: {video_path}")
            
            # Extract audio from video
            audio_path = await self._extract_audio_from_video(video_path)
            
            # Analyze audio
            analysis_result = await self._analyze_audio(audio_path)
            
            # Clean up temporary files
            try:
                Path(audio_path).unlink()
            except:
                pass
            
            logger.info(f"Audio processing completed: {len(analysis_result.segments)} segments")
            return analysis_result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path, "operation": "process_video_audio"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio from video file"""
        try:
            # Create temporary audio file
            temp_audio = self.temp_dir / f"audio_{Path(video_path).stem}.wav"
            
            # Extract audio using FFmpeg
            success = AudioUtils.extract_audio_from_video(video_path, str(temp_audio))
            
            if not success:
                raise RuntimeError(f"Failed to extract audio from {video_path}")
            
            logger.info(f"Audio extracted to: {temp_audio}")
            return str(temp_audio)
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _analyze_audio(self, audio_path: str) -> AudioAnalysisResult:
        """Analyze audio file and extract segments"""
        try:
            # Load audio file
            audio_data, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            
            # Get audio info
            info = AudioUtils.get_audio_info(audio_path)
            
            # Split audio into segments
            segments = await self._split_audio_segments(audio_data, sr)
            
            # Analyze audio quality
            audio_quality = await self._analyze_audio_quality(audio_data, sr)
            
            # Detect language
            language = await self._detect_language(audio_data, sr)
            
            # Detect speakers
            speakers = await self._detect_speakers(audio_data, sr, segments)
            
            analysis_result = AudioAnalysisResult(
                segments=segments,
                total_duration=len(audio_data) / sr,
                sample_rate=sr,
                channels=1,
                format=info.get('format', 'wav'),
                speakers=speakers,
                language=language,
                audio_quality=audio_quality
            )
            
            logger.info(f"Audio analysis completed: {len(segments)} segments, {len(speakers)} speakers")
            return analysis_result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"audio_path": audio_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _split_audio_segments(self, audio_data: np.ndarray, sr: int) -> List[AudioSegment]:
        """Split audio into segments"""
        try:
            segments = []
            
            # Use librosa to detect silence and split
            intervals = librosa.effects.split(
                audio_data, 
                top_db=settings.audio.silence_threshold,
                frame_length=settings.audio.frame_length,
                hop_length=settings.audio.hop_length
            )
            
            # Create segments from intervals
            for i, (start, end) in enumerate(intervals):
                start_time = start / sr
                end_time = end / sr
                duration = end_time - start_time
                
                # Skip very short segments
                if duration < settings.audio.min_segment_duration:
                    continue
                
                segment = AudioSegment(
                    id=f"segment_{i:03d}",
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    audio_data=audio_data[start:end],
                    sample_rate=sr
                )
                
                segments.append(segment)
            
            logger.info(f"Split audio into {len(segments)} segments")
            return segments
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "split_audio_segments"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _analyze_audio_quality(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze audio quality metrics"""
        try:
            quality_metrics = {}
            
            # Calculate SNR (Signal-to-Noise Ratio)
            signal_power = np.mean(audio_data ** 2)
            noise_floor = np.mean(audio_data ** 2) * 0.01  # Estimate noise
            snr = 10 * np.log10(signal_power / noise_floor) if noise_floor > 0 else 60
            quality_metrics['snr_db'] = snr
            
            # Calculate RMS energy
            rms = np.sqrt(np.mean(audio_data ** 2))
            quality_metrics['rms_energy'] = float(rms)
            
            # Calculate zero crossing rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data))
            quality_metrics['zero_crossing_rate'] = float(zcr)
            
            # Calculate spectral centroid
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr))
            quality_metrics['spectral_centroid'] = float(spectral_centroid)
            
            # Calculate MFCC coefficients
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            quality_metrics['mfcc_mean'] = float(np.mean(mfccs))
            
            logger.info(f"Audio quality analysis completed: SNR={snr:.2f}dB")
            return quality_metrics
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "analyze_audio_quality"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return {}
    
    async def _detect_language(self, audio_data: np.ndarray, sr: int) -> Optional[str]:
        """Detect language from audio"""
        try:
            # This is a simplified language detection
            # In practice, you would use a proper language detection model
            
            # Extract features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            mfccs_mean = np.mean(mfccs, axis=1)
            
            # Simple heuristic based on MFCC patterns
            # This is just a placeholder - replace with actual language detection
            if mfccs_mean[0] > 0:
                return "zh"  # Chinese
            else:
                return "en"  # English
                
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "detect_language"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return None
    
    async def _detect_speakers(self, audio_data: np.ndarray, sr: int, segments: List[AudioSegment]) -> List[str]:
        """Detect different speakers in audio"""
        try:
            # This is a simplified speaker detection
            # In practice, you would use proper speaker diarization
            
            speakers = []
            speaker_id = 0
            
            for segment in segments:
                # Extract features for this segment
                segment_audio = audio_data[int(segment.start_time * sr):int(segment.end_time * sr)]
                
                if len(segment_audio) == 0:
                    continue
                
                # Calculate MFCCs for speaker characterization
                mfccs = librosa.feature.mfcc(y=segment_audio, sr=sr, n_mfcc=13)
                mfccs_mean = np.mean(mfccs, axis=1)
                
                # Simple heuristic to determine if this is a new speaker
                # This is just a placeholder - replace with actual speaker diarization
                if len(speakers) == 0 or speaker_id >= 4:  # Limit to 4 speakers for demo
                    speakers.append(f"speaker_{speaker_id}")
                    segment.speaker_id = f"speaker_{speaker_id}"
                    speaker_id += 1
                else:
                    # Assign to existing speaker
                    segment.speaker_id = speakers[speaker_id % len(speakers)]
            
            logger.info(f"Detected {len(speakers)} speakers")
            return speakers
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "detect_speakers"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return []
    
    async def preprocess_audio(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """Preprocess audio data"""
        try:
            # Normalize audio
            audio_data = librosa.util.normalize(audio_data)
            
            # Apply noise reduction if needed
            if settings.audio.enable_noise_reduction:
                audio_data = await self._reduce_noise(audio_data, sr)
            
            # Apply equalization
            if settings.audio.enable_equalization:
                audio_data = await self._apply_equalization(audio_data, sr)
            
            return audio_data
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "preprocess_audio"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return audio_data
    
    async def _reduce_noise(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """Reduce noise from audio"""
        try:
            # Simple noise reduction using spectral gating
            # This is a basic implementation - consider using specialized libraries
            
            # Compute STFT
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor
            noise_floor = np.mean(magnitude[:, :10], axis=1, keepdims=True)
            
            # Apply noise gate
            threshold = noise_floor * 2
            magnitude_clean = np.where(magnitude > threshold, magnitude - threshold, 0)
            
            # Reconstruct signal
            stft_clean = magnitude_clean * np.exp(1j * phase)
            audio_clean = librosa.istft(stft_clean)
            
            return audio_clean
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "reduce_noise"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.LOW
            )
            return audio_data
    
    async def _apply_equalization(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """Apply equalization to audio"""
        try:
            # Simple equalization using frequency filters
            
            # Apply high-pass filter to remove low frequency noise
            audio_data = librosa.effects.preemphasis(audio_data)
            
            # Apply low-pass filter to remove high frequency noise
            cutoff_freq = min(8000, sr // 2)
            nyquist = sr // 2
            normal_cutoff = cutoff_freq / nyquist
            
            # Simple FIR filter
            from scipy import signal
            b, a = signal.butter(5, normal_cutoff, btype='low')
            audio_data = signal.filtfilt(b, a, audio_data)
            
            return audio_data
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "apply_equalization"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.LOW
            )
            return audio_data
    
    async def save_audio_segment(self, segment: AudioSegment, output_path: str) -> bool:
        """Save audio segment to file"""
        try:
            if segment.audio_data is None:
                raise ValueError("No audio data in segment")
            
            # Save using soundfile
            sf.write(output_path, segment.audio_data, segment.sample_rate)
            
            logger.log_file_operation("save_audio_segment", output_path, 
                                    Path(output_path).stat().st_size if Path(output_path).exists() else 0)
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"segment_id": segment.id, "output_path": output_path},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    async def batch_process_segments(self, segments: List[AudioSegment], 
                                   process_func: callable) -> List[AudioSegment]:
        """Batch process multiple audio segments"""
        try:
            processed_segments = []
            
            # Process segments in batches
            batch_size = settings.audio.batch_size
            
            for i in range(0, len(segments), batch_size):
                batch = segments[i:i + batch_size]
                
                # Process batch asynchronously
                tasks = [process_func(segment) for segment in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle results
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing segment {batch[j].id}: {result}")
                        # Keep original segment if processing fails
                        processed_segments.append(batch[j])
                    else:
                        processed_segments.append(result)
                
                # Update progress
                progress = min((i + len(batch)) / len(segments), 1.0)
                logger.info(f"Batch processing progress: {progress:.2%}")
            
            return processed_segments
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "batch_process_segments", "segment_count": len(segments)},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return segments


# Create singleton instance
audio_processing_service = AudioProcessingService()
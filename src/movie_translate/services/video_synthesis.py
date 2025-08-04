"""
Video synthesis service for Movie Translate
"""

import asyncio
import numpy as np
import cv2
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import tempfile
import json

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity, cache_manager
from ..utils.audio_utils import AudioUtils
from ..utils.file_utils import FileUtils
from .audio_processing import AudioAnalysisResult, AudioSegment
from .voice_cloning import VoiceCloningResult


@dataclass
class VideoSynthesisResult:
    """Video synthesis result"""
    output_path: str
    original_video_path: str
    audio_path: str
    duration: float
    resolution: Tuple[int, int]
    fps: float
    file_size: int
    processing_time: float
    quality_metrics: Dict[str, float] = None


@dataclass
class VideoSegment:
    """Video segment data"""
    start_time: float
    end_time: float
    audio_path: str
    video_path: str
    text: str
    character_id: str
    duration: float


class VideoSynthesisService:
    """Video synthesis service for movie translation"""
    
    def __init__(self):
        self.temp_dir = settings.get_temp_path()
        self.output_dir = settings.get_cache_path() / "output_videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Video processing settings
        self.target_resolution = settings.video.target_resolution
        self.target_fps = settings.video.target_fps
        self.target_bitrate = settings.video.target_bitrate
        self.target_codec = settings.video.target_codec
        
    async def synthesize_video(self, original_video_path: str, 
                             audio_analysis: AudioAnalysisResult,
                             cloned_audio_results: List[VoiceCloningResult],
                             output_path: str) -> VideoSynthesisResult:
        """Synthesize final video with translated audio"""
        try:
            logger.info(f"Starting video synthesis: {original_video_path}")
            
            start_time = datetime.now()
            
            # Validate inputs
            if not Path(original_video_path).exists():
                raise FileNotFoundError(f"Original video not found: {original_video_path}")
            
            if not cloned_audio_results:
                raise ValueError("No cloned audio results provided")
            
            # Prepare audio segments
            audio_segments = await self._prepare_audio_segments(cloned_audio_results)
            
            # Merge audio segments
            merged_audio_path = await self._merge_audio_segments(audio_segments)
            
            # Synchronize audio with video
            synchronized_audio = await self._synchronize_audio_video(
                original_video_path, merged_audio_path
            )
            
            # Create final video
            final_video_path = await self._create_final_video(
                original_video_path, synchronized_audio, output_path
            )
            
            # Analyze video quality
            quality_metrics = await self._analyze_video_quality(final_video_path)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Get video info
            video_info = await self._get_video_info(final_video_path)
            
            # Create result
            result = VideoSynthesisResult(
                output_path=final_video_path,
                original_video_path=original_video_path,
                audio_path=synchronized_audio,
                duration=video_info['duration'],
                resolution=video_info['resolution'],
                fps=video_info['fps'],
                file_size=video_info['file_size'],
                processing_time=processing_time,
                quality_metrics=quality_metrics
            )
            
            logger.info(f"Video synthesis completed: {final_video_path}")
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"original_video_path": original_video_path, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _prepare_audio_segments(self, cloned_results: List[VoiceCloningResult]) -> List[Dict[str, Any]]:
        """Prepare audio segments for processing"""
        try:
            segments = []
            
            for result in cloned_results:
                # Get audio duration
                duration = result.duration
                
                # Create segment info
                segment = {
                    'audio_path': result.audio_path,
                    'text': result.text,
                    'character_id': result.character_id,
                    'duration': duration,
                    'start_time': 0.0,  # Will be calculated during merging
                    'end_time': duration
                }
                
                segments.append(segment)
            
            logger.info(f"Prepared {len(segments)} audio segments")
            return segments
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "prepare_audio_segments"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _merge_audio_segments(self, segments: List[Dict[str, Any]]) -> str:
        """Merge audio segments into single file"""
        try:
            # Create temporary file for merged audio
            merged_audio_path = self.temp_dir / "merged_audio.wav"
            
            # Calculate timing for each segment
            current_time = 0.0
            for segment in segments:
                segment['start_time'] = current_time
                segment['end_time'] = current_time + segment['duration']
                current_time += segment['duration']
            
            # Merge audio files with proper timing
            success = await self._merge_audio_with_timing(segments, str(merged_audio_path))
            
            if not success:
                raise RuntimeError("Failed to merge audio segments")
            
            logger.info(f"Audio segments merged: {len(segments)} segments")
            return str(merged_audio_path)
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "merge_audio_segments"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _merge_audio_with_timing(self, segments: List[Dict[str, Any]], 
                                     output_path: str) -> bool:
        """Merge audio segments with proper timing"""
        try:
            import subprocess
            
            # Create FFmpeg filter complex for merging
            filter_parts = []
            inputs = []
            
            for i, segment in enumerate(segments):
                # Add input file
                inputs.extend(['-i', segment['audio_path']])
                
                # Create filter for this segment
                filter_parts.append(f"[{i}:a]adelay={int(segment['start_time'] * 1000)}|1000[delayed_{i}]")
            
            # Mix all delayed audio streams
            filter_parts.append("".join([f"[delayed_{i}]" for i in range(len(segments))]))
            filter_parts.append(f"amix=inputs={len(segments)}:duration=longest[mixed]")
            
            # Build FFmpeg command
            cmd = ['ffmpeg'] + inputs + ['-filter_complex', ''.join(filter_parts)]
            cmd.extend(['-map', '[mixed]', '-c:a', 'pcm_s16le', '-y', output_path])
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.info("Audio segments merged with timing")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "merge_audio_with_timing"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    async def _synchronize_audio_video(self, video_path: str, audio_path: str) -> str:
        """Synchronize audio with video"""
        try:
            # Create synchronized audio file
            synchronized_audio = self.temp_dir / "synchronized_audio.wav"
            
            # Get video duration
            video_duration = await self._get_video_duration(video_path)
            audio_duration = await self._get_audio_duration(audio_path)
            
            # Adjust audio duration to match video
            if audio_duration < video_duration:
                # Pad audio with silence
                success = await self._pad_audio_with_silence(
                    audio_path, str(synchronized_audio), video_duration
                )
            elif audio_duration > video_duration:
                # Trim audio to match video
                success = await self._trim_audio_to_duration(
                    audio_path, str(synchronized_audio), video_duration
                )
            else:
                # No adjustment needed
                synchronized_audio = Path(audio_path)
                success = True
            
            if not success:
                raise RuntimeError("Failed to synchronize audio with video")
            
            logger.info(f"Audio synchronized with video: {video_duration}s")
            return str(synchronized_audio)
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path, "audio_path": audio_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _pad_audio_with_silence(self, input_path: str, output_path: str, 
                                    target_duration: float) -> bool:
        """Pad audio with silence to match target duration"""
        try:
            import subprocess
            
            # Get current audio duration
            current_duration = await self._get_audio_duration(input_path)
            silence_duration = target_duration - current_duration
            
            if silence_duration <= 0:
                return True
            
            # Create silence
            silence_filter = f"aevalsrc=0:d={silence_duration}[silence]"
            
            # Mix original audio with silence
            cmd = [
                'ffmpeg', '-i', input_path, '-f', 'lavfi', '-i', silence_filter,
                '-filter_complex', '[0:a][1:a]concat=n=2:v=0:a=1[out]',
                '-map', '[out]', '-c:a', 'pcm_s16le', '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.info(f"Audio padded with {silence_duration}s silence")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"input_path": input_path, "target_duration": target_duration},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    async def _trim_audio_to_duration(self, input_path: str, output_path: str, 
                                    target_duration: float) -> bool:
        """Trim audio to match target duration"""
        try:
            import subprocess
            
            cmd = [
                'ffmpeg', '-i', input_path, '-t', str(target_duration),
                '-c:a', 'pcm_s16le', '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.info(f"Audio trimmed to {target_duration}s")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"input_path": input_path, "target_duration": target_duration},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    async def _create_final_video(self, video_path: str, audio_path: str, 
                                output_path: str) -> str:
        """Create final video with translated audio"""
        try:
            import subprocess
            
            # Get video info
            video_info = await self._get_video_info(video_path)
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-i', video_path, '-i', audio_path,
                '-c:v', self.target_codec,
                '-c:a', 'aac',
                '-b:v', self.target_bitrate,
                '-r', str(self.target_fps),
                '-map', '0:v:0',  # Video from original
                '-map', '1:a:0',  # Audio from translated
                '-shortest',  # Use shortest duration
                '-y', output_path
            ]
            
            # Add scaling if needed
            if self.target_resolution:
                scale_filter = f"scale={self.target_resolution[0]}:{self.target_resolution[1]}"
                cmd.extend(['-vf', scale_filter])
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise RuntimeError("Failed to create final video")
            
            logger.info(f"Final video created: {output_path}")
            return output_path
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path, "audio_path": audio_path, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _get_video_duration(self, video_path: str) -> float:
        """Get video duration"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError("Could not open video file")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            cap.release()
            
            if fps > 0:
                return frame_count / fps
            else:
                return 0.0
                
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return 0.0
    
    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration"""
        try:
            import librosa
            
            audio_data, sr = librosa.load(audio_path, sr=None)
            return len(audio_data) / sr
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"audio_path": audio_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return 0.0
    
    async def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video information"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError("Could not open video file")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            
            # Get file size
            file_size = Path(video_path).stat().st_size
            
            # Calculate duration
            duration = frame_count / fps if fps > 0 else 0.0
            
            return {
                'duration': duration,
                'resolution': (width, height),
                'fps': fps,
                'frame_count': frame_count,
                'file_size': file_size
            }
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return {}
    
    async def _analyze_video_quality(self, video_path: str) -> Dict[str, float]:
        """Analyze video quality"""
        try:
            quality_metrics = {}
            
            # Get video info
            video_info = await self._get_video_info(video_path)
            
            if not video_info:
                return quality_metrics
            
            # Basic metrics
            quality_metrics['resolution_width'] = video_info['resolution'][0]
            quality_metrics['resolution_height'] = video_info['resolution'][1]
            quality_metrics['fps'] = video_info['fps']
            quality_metrics['duration'] = video_info['duration']
            quality_metrics['file_size_mb'] = video_info['file_size'] / (1024 * 1024)
            
            # Calculate bitrate
            if video_info['duration'] > 0:
                bitrate = (video_info['file_size'] * 8) / video_info['duration']  # bits per second
                quality_metrics['bitrate_kbps'] = bitrate / 1000
            
            # Analyze frame quality (sample analysis)
            quality_metrics.update(await self._analyze_frame_quality(video_path))
            
            return quality_metrics
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return {}
    
    async def _analyze_frame_quality(self, video_path: str) -> Dict[str, float]:
        """Analyze video frame quality"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {}
            
            # Sample frames for analysis
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_frames = min(10, total_frames)
            frame_indices = np.linspace(0, total_frames - 1, sample_frames, dtype=int)
            
            brightness_scores = []
            contrast_scores = []
            blur_scores = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Calculate brightness
                    brightness = np.mean(gray)
                    brightness_scores.append(brightness)
                    
                    # Calculate contrast
                    contrast = np.std(gray)
                    contrast_scores.append(contrast)
                    
                    # Calculate blur (using Laplacian variance)
                    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
                    blur_scores.append(blur)
            
            cap.release()
            
            if brightness_scores:
                return {
                    'avg_brightness': float(np.mean(brightness_scores)),
                    'avg_contrast': float(np.mean(contrast_scores)),
                    'avg_blur_score': float(np.mean(blur_scores))
                }
            
            return {}
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.LOW
            )
            return {}
    
    async def create_video_preview(self, video_path: str, output_path: str, 
                                 duration: float = 10.0) -> bool:
        """Create video preview"""
        try:
            import subprocess
            
            # Create preview from first N seconds
            cmd = [
                'ffmpeg', '-i', video_path, '-t', str(duration),
                '-c:v', self.target_codec,
                '-c:a', 'aac',
                '-b:v', self.target_bitrate,
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.info(f"Video preview created: {output_path}")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    async def extract_thumbnail(self, video_path: str, output_path: str, 
                               time_offset: float = 1.0) -> bool:
        """Extract thumbnail from video"""
        try:
            import subprocess
            
            cmd = [
                'ffmpeg', '-i', video_path, '-ss', str(time_offset),
                '-vframes', '1', '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.info(f"Thumbnail extracted: {output_path}")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return False


# Create singleton instance
video_synthesis_service = VideoSynthesisService()
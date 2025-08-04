"""
Audio utilities for Movie Translate
"""

import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import tempfile
import subprocess

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity


class AudioUtils:
    """Audio utility functions"""
    
    @staticmethod
    def extract_audio_from_video(video_path: str, output_path: str) -> bool:
        """Extract audio from video file"""
        try:
            cmd = [
                'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
                '-ar', str(settings.audio.sample_rate), '-ac', str(settings.audio.channels),
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.log_file_operation("audio_extract", video_path, 
                                    Path(output_path).stat().st_size if Path(output_path).exists() else 0)
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    @staticmethod
    def convert_audio_format(input_path: str, output_path: str, 
                           format: str = "wav", sample_rate: int = 16000) -> bool:
        """Convert audio format"""
        try:
            cmd = [
                'ffmpeg', '-i', input_path, '-ar', str(sample_rate), '-ac', '1',
                '-c:a', 'pcm_s16le' if format == 'wav' else 'libmp3lame',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.log_file_operation("audio_convert", input_path, 
                                    Path(output_path).stat().st_size if Path(output_path).exists() else 0)
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"input_path": input_path, "output_path": output_path, "format": format},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    @staticmethod
    def normalize_audio(audio_path: str, output_path: str) -> bool:
        """Normalize audio volume"""
        try:
            cmd = [
                'ffmpeg', '-i', audio_path, '-filter:a', 'loudnorm=I=-16:LRA=11:TP=-1.5',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.log_file_operation("audio_normalize", audio_path,
                                    Path(output_path).stat().st_size if Path(output_path).exists() else 0)
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"audio_path": audio_path, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    @staticmethod
    def reduce_noise(audio_path: str, output_path: str) -> bool:
        """Reduce noise from audio"""
        try:
            cmd = [
                'ffmpeg', '-i', audio_path, '-af', 'highpass=200,lowpass=3000',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.log_file_operation("audio_denoise", audio_path,
                                    Path(output_path).stat().st_size if Path(output_path).exists() else 0)
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"audio_path": audio_path, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    @staticmethod
    def split_audio_by_silence(audio_path: str, output_dir: str, 
                             min_silence_len: int = 1000, 
                             silence_thresh: int = -40) -> List[str]:
        """Split audio by silence"""
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                'ffmpeg', '-i', audio_path, '-af',
                f'silencedetect=noise={silence_thresh}dB:d={min_silence_len/1000}',
                '-f', 'null', '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return []
            
            # Parse silence detection results
            silence_times = []
            for line in result.stderr.split('\n'):
                if 'silence_start' in line:
                    start_time = float(line.split('silence_start: ')[1])
                    silence_times.append(('start', start_time))
                elif 'silence_end' in line:
                    end_time = float(line.split('silence_end: ')[1])
                    silence_times.append(('end', end_time))
            
            # Split audio based on silence detection
            segments = []
            current_start = 0
            
            for i in range(0, len(silence_times), 2):
                if i + 1 < len(silence_times):
                    end_time = silence_times[i][1]
                    next_start = silence_times[i + 1][1]
                    
                    if end_time - current_start > 1.0:  # Minimum segment length
                        output_path = output_dir / f"segment_{len(segments):03d}.wav"
                        
                        cmd = [
                            'ffmpeg', '-i', audio_path, '-ss', str(current_start),
                            '-to', str(end_time), '-c', 'copy', '-y', str(output_path)
                        ]
                        
                        subprocess.run(cmd, capture_output=True)
                        
                        if output_path.exists():
                            segments.append(str(output_path))
                    
                    current_start = next_start
            
            logger.info(f"Split audio into {len(segments)} segments")
            return segments
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"audio_path": audio_path, "output_dir": output_dir},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return []
    
    @staticmethod
    def get_audio_info(audio_path: str) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            import soundfile as sf
            
            with sf.SoundFile(audio_path) as audio_file:
                info = {
                    'samplerate': audio_file.samplerate,
                    'channels': audio_file.channels,
                    'frames': len(audio_file),
                    'duration': len(audio_file) / audio_file.samplerate,
                    'format': audio_file.format,
                    'subtype': audio_file.subtype
                }
                
                logger.log_file_operation("audio_info", audio_path)
                return info
                
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"audio_path": audio_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return {}
    
    @staticmethod
    def mix_audio_files(audio_files: List[str], output_path: str) -> bool:
        """Mix multiple audio files"""
        try:
            if not audio_files:
                return False
            
            # Create input filter for mixing
            filter_parts = []
            for i, audio_file in enumerate(audio_files):
                filter_parts.append(f"[{i}:a]")
            
            filter_complex = f"{''.join(filter_parts)}amix=inputs={len(audio_files)}:duration=longest"
            
            cmd = ['ffmpeg']
            
            # Add input files
            for audio_file in audio_files:
                cmd.extend(['-i', audio_file])
            
            # Add filter and output
            cmd.extend(['-filter_complex', filter_complex, '-y', output_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.log_file_operation("audio_mix", f"{len(audio_files)} files",
                                    Path(output_path).stat().st_size if Path(output_path).exists() else 0)
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"audio_files": audio_files, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    @staticmethod
    def adjust_audio_speed(audio_path: str, output_path: str, speed_factor: float) -> bool:
        """Adjust audio playback speed"""
        try:
            cmd = [
                'ffmpeg', '-i', audio_path, '-filter:a', f'atempo={speed_factor}',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.log_file_operation("audio_speed", audio_path,
                                    Path(output_path).stat().st_size if Path(output_path).exists() else 0,
                                    speed_factor=speed_factor)
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"audio_path": audio_path, "output_path": output_path, "speed_factor": speed_factor},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
    
    @staticmethod
    def merge_audio_with_video(video_path: str, audio_path: str, output_path: str) -> bool:
        """Merge audio with video"""
        try:
            cmd = [
                'ffmpeg', '-i', video_path, '-i', audio_path,
                '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
                '-shortest', '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            logger.log_file_operation("audio_video_merge", f"{video_path} + {audio_path}",
                                    Path(output_path).stat().st_size if Path(output_path).exists() else 0)
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"video_path": video_path, "audio_path": audio_path, "output_path": output_path},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False
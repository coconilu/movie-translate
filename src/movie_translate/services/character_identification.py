"""
Character identification service for Movie Translate
"""

import asyncio
import numpy as np
import librosa
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pickle
import tempfile

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity, cache_manager
from .audio_processing import AudioSegment, AudioAnalysisResult


@dataclass
class VoiceProfile:
    """Voice profile for character identification"""
    character_id: str
    character_name: str
    voice_features: np.ndarray
    sample_rate: int
    segments_count: int
    avg_duration: float
    language: str
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'character_id': self.character_id,
            'character_name': self.character_name,
            'voice_features': self.voice_features.tolist(),
            'sample_rate': self.sample_rate,
            'segments_count': self.segments_count,
            'avg_duration': self.avg_duration,
            'language': self.language,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceProfile':
        """Create from dictionary"""
        return cls(
            character_id=data['character_id'],
            character_name=data['character_name'],
            voice_features=np.array(data['voice_features']),
            sample_rate=data['sample_rate'],
            segments_count=data['segments_count'],
            avg_duration=data['avg_duration'],
            language=data['language'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


@dataclass
class CharacterIdentificationResult:
    """Character identification result"""
    segment_id: str
    character_id: str
    character_name: str
    confidence: float
    voice_features: np.ndarray
    alternative_matches: List[Dict[str, Any]]


class CharacterIdentificationService:
    """Character identification service"""
    
    def __init__(self):
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.profile_dir = settings.get_cache_path() / "voice_profiles"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing profiles
        self._load_voice_profiles()
        
        # Voice feature extraction parameters
        self.n_mfcc = 20
        self.n_mels = 128
        self.hop_length = 512
        self.n_fft = 2048
        
    async def identify_characters(self, audio_analysis: AudioAnalysisResult) -> AudioAnalysisResult:
        """Identify characters in audio segments"""
        try:
            logger.info(f"Starting character identification for {len(audio_analysis.segments)} segments")
            
            # Group segments by initial speaker ID
            speaker_groups = self._group_segments_by_speaker(audio_analysis.segments)
            
            # Identify characters for each speaker group
            character_results = {}
            for speaker_id, segments in speaker_groups.items():
                logger.info(f"Processing speaker group: {speaker_id} ({len(segments)} segments)")
                
                # Extract voice features for this speaker
                voice_features = await self._extract_voice_features(segments)
                
                # Identify character
                character_result = await self._identify_character(voice_features, segments)
                
                # Update segments with character information
                for segment in segments:
                    segment.speaker_id = character_result.character_id
                    segment.confidence = character_result.confidence
                
                character_results[speaker_id] = character_result
            
            # Save voice profiles for new characters
            await self._save_new_voice_profiles(character_results)
            
            logger.info("Character identification completed")
            return audio_analysis
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "identify_characters", "segment_count": len(audio_analysis.segments)},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _group_segments_by_speaker(self, segments: List[AudioSegment]) -> Dict[str, List[AudioSegment]]:
        """Group segments by speaker ID"""
        groups = {}
        for segment in segments:
            speaker_id = segment.speaker_id or "unknown"
            if speaker_id not in groups:
                groups[speaker_id] = []
            groups[speaker_id].append(segment)
        return groups
    
    async def _extract_voice_features(self, segments: List[AudioSegment]) -> np.ndarray:
        """Extract voice features from segments"""
        try:
            all_features = []
            
            for segment in segments:
                if segment.audio_data is None or len(segment.audio_data) == 0:
                    continue
                
                # Extract MFCC features
                mfccs = librosa.feature.mfcc(
                    y=segment.audio_data,
                    sr=segment.sample_rate,
                    n_mfcc=self.n_mfcc,
                    hop_length=self.hop_length,
                    n_fft=self.n_fft
                )
                
                # Extract spectral features
                spectral_centroids = librosa.feature.spectral_centroid(
                    y=segment.audio_data,
                    sr=segment.sample_rate,
                    hop_length=self.hop_length
                )
                
                # Extract chroma features
                chroma = librosa.feature.chroma_stft(
                    y=segment.audio_data,
                    sr=segment.sample_rate,
                    hop_length=self.hop_length
                )
                
                # Extract zero crossing rate
                zcr = librosa.feature.zero_crossing_rate(
                    y=segment.audio_data,
                    hop_length=self.hop_length
                )
                
                # Combine features
                features = np.concatenate([
                    np.mean(mfccs, axis=1),
                    np.std(mfccs, axis=1),
                    np.mean(spectral_centroids),
                    np.std(spectral_centroids),
                    np.mean(chroma, axis=1),
                    np.std(chroma, axis=1),
                    np.mean(zcr),
                    np.std(zcr)
                ])
                
                all_features.append(features)
            
            if not all_features:
                raise ValueError("No voice features extracted")
            
            # Return average features
            return np.mean(all_features, axis=0)
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "extract_voice_features", "segment_count": len(segments)},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _identify_character(self, voice_features: np.ndarray, 
                                segments: List[AudioSegment]) -> CharacterIdentificationResult:
        """Identify character from voice features"""
        try:
            if not self.voice_profiles:
                # No existing profiles, create new character
                return await self._create_new_character(voice_features, segments)
            
            # Compare with existing profiles
            best_match = None
            best_confidence = 0.0
            alternative_matches = []
            
            for character_id, profile in self.voice_profiles.items():
                similarity = self._calculate_voice_similarity(voice_features, profile.voice_features)
                
                match_info = {
                    'character_id': character_id,
                    'character_name': profile.character_name,
                    'confidence': similarity
                }
                alternative_matches.append(match_info)
                
                if similarity > best_confidence:
                    best_confidence = similarity
                    best_match = profile
            
            # Sort alternatives by confidence
            alternative_matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Check if match is confident enough
            if best_confidence > settings.character.similarity_threshold:
                return CharacterIdentificationResult(
                    segment_id=segments[0].id if segments else "unknown",
                    character_id=best_match.character_id,
                    character_name=best_match.character_name,
                    confidence=best_confidence,
                    voice_features=voice_features,
                    alternative_matches=alternative_matches[:3]  # Top 3 alternatives
                )
            else:
                # Create new character
                return await self._create_new_character(voice_features, segments)
                
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "identify_character"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _calculate_voice_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate similarity between voice features"""
        try:
            # Normalize features
            features1_norm = features1 / (np.linalg.norm(features1) + 1e-8)
            features2_norm = features2 / (np.linalg.norm(features2) + 1e-8)
            
            # Calculate cosine similarity
            similarity = np.dot(features1_norm, features2_norm)
            
            # Apply distance weighting
            distance = np.linalg.norm(features1 - features2)
            distance_weight = np.exp(-distance / 10.0)
            
            # Combined similarity score
            combined_similarity = similarity * distance_weight
            
            return max(0.0, min(1.0, combined_similarity))
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "calculate_voice_similarity"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return 0.0
    
    async def _create_new_character(self, voice_features: np.ndarray, 
                                  segments: List[AudioSegment]) -> CharacterIdentificationResult:
        """Create new character from voice features"""
        try:
            # Generate character ID
            character_id = f"character_{len(self.voice_profiles) + 1:03d}"
            
            # Generate character name
            character_name = f"角色{len(self.voice_profiles) + 1}"
            
            # Calculate average duration
            avg_duration = np.mean([s.duration for s in segments])
            
            # Detect language
            language = segments[0].language if segments and segments[0].language else "zh"
            
            # Create voice profile
            now = datetime.now()
            profile = VoiceProfile(
                character_id=character_id,
                character_name=character_name,
                voice_features=voice_features,
                sample_rate=segments[0].sample_rate if segments else 16000,
                segments_count=len(segments),
                avg_duration=avg_duration,
                language=language,
                created_at=now,
                updated_at=now
            )
            
            # Add to profiles
            self.voice_profiles[character_id] = profile
            
            logger.info(f"Created new character: {character_name} ({character_id})")
            
            return CharacterIdentificationResult(
                segment_id=segments[0].id if segments else "unknown",
                character_id=character_id,
                character_name=character_name,
                confidence=1.0,  # New character has perfect confidence
                voice_features=voice_features,
                alternative_matches=[]
            )
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "create_new_character"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _save_new_voice_profiles(self, character_results: Dict[str, CharacterIdentificationResult]):
        """Save new voice profiles"""
        try:
            for result in character_results.values():
                if result.character_id in self.voice_profiles:
                    # Save profile to disk
                    await self._save_voice_profile(self.voice_profiles[result.character_id])
                    
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "save_new_voice_profiles"},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
    
    async def _save_voice_profile(self, profile: VoiceProfile):
        """Save voice profile to disk"""
        try:
            profile_path = self.profile_dir / f"{profile.character_id}.pkl"
            
            with open(profile_path, 'wb') as f:
                pickle.dump(profile.to_dict(), f)
            
            logger.info(f"Voice profile saved: {profile.character_name}")
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"character_id": profile.character_id},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
    
    def _load_voice_profiles(self):
        """Load voice profiles from disk"""
        try:
            for profile_file in self.profile_dir.glob("*.pkl"):
                try:
                    with open(profile_file, 'rb') as f:
                        profile_data = pickle.load(f)
                    
                    profile = VoiceProfile.from_dict(profile_data)
                    self.voice_profiles[profile.character_id] = profile
                    
                except Exception as e:
                    logger.warning(f"Failed to load voice profile {profile_file}: {e}")
                    continue
            
            logger.info(f"Loaded {len(self.voice_profiles)} voice profiles")
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "load_voice_profiles"},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
    
    async def update_character_name(self, character_id: str, new_name: str) -> bool:
        """Update character name"""
        try:
            if character_id not in self.voice_profiles:
                return False
            
            profile = self.voice_profiles[character_id]
            profile.character_name = new_name
            profile.updated_at = datetime.now()
            
            # Save updated profile
            await self._save_voice_profile(profile)
            
            logger.info(f"Character name updated: {character_id} -> {new_name}")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"character_id": character_id, "new_name": new_name},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    async def delete_character(self, character_id: str) -> bool:
        """Delete character profile"""
        try:
            if character_id not in self.voice_profiles:
                return False
            
            # Remove from memory
            del self.voice_profiles[character_id]
            
            # Remove from disk
            profile_path = self.profile_dir / f"{character_id}.pkl"
            if profile_path.exists():
                profile_path.unlink()
            
            logger.info(f"Character deleted: {character_id}")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"character_id": character_id},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Get all character profiles"""
        try:
            characters = []
            for profile in self.voice_profiles.values():
                characters.append({
                    'character_id': profile.character_id,
                    'character_name': profile.character_name,
                    'segments_count': profile.segments_count,
                    'avg_duration': profile.avg_duration,
                    'language': profile.language,
                    'created_at': profile.created_at.isoformat(),
                    'updated_at': profile.updated_at.isoformat()
                })
            
            return sorted(characters, key=lambda x: x['created_at'])
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "get_all_characters"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return []
    
    async def merge_characters(self, character_ids: List[str], new_name: str) -> bool:
        """Merge multiple characters into one"""
        try:
            if len(character_ids) < 2:
                return False
            
            # Get profiles for all characters
            profiles = [self.voice_profiles[cid] for cid in character_ids if cid in self.voice_profiles]
            
            if len(profiles) < 2:
                return False
            
            # Create merged profile
            merged_features = np.mean([p.voice_features for p in profiles], axis=0)
            merged_segments = sum(p.segments_count for p in profiles)
            merged_duration = np.mean([p.avg_duration for p in profiles])
            
            # Create new character ID
            new_character_id = f"character_{len(self.voice_profiles) + 1:03d}"
            
            # Create merged profile
            now = datetime.now()
            merged_profile = VoiceProfile(
                character_id=new_character_id,
                character_name=new_name,
                voice_features=merged_features,
                sample_rate=profiles[0].sample_rate,
                segments_count=merged_segments,
                avg_duration=merged_duration,
                language=profiles[0].language,
                created_at=now,
                updated_at=now
            )
            
            # Remove old profiles
            for character_id in character_ids:
                await self.delete_character(character_id)
            
            # Add merged profile
            self.voice_profiles[new_character_id] = merged_profile
            await self._save_voice_profile(merged_profile)
            
            logger.info(f"Characters merged: {character_ids} -> {new_name}")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"character_ids": character_ids, "new_name": new_name},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            return False


# Create singleton instance
character_identification_service = CharacterIdentificationService()
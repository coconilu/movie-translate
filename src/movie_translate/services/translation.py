"""
Translation service for Movie Translate
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

from ..core import logger, settings, error_handler, ErrorCategory, ErrorSeverity, cache_manager
from .audio_processing import AudioAnalysisResult, AudioSegment


class TranslationResult:
    """Translation result"""
    
    def __init__(self, original_text: str, translated_text: str, 
                 source_lang: str, target_lang: str, confidence: float = 0.0,
                 alternatives: List[Dict] = None):
        self.original_text = original_text
        self.translated_text = translated_text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.confidence = confidence
        self.alternatives = alternatives or []
        self.timestamp = datetime.now()


class DeepSeekTranslation:
    """DeepSeek translation service"""
    
    def __init__(self):
        self.api_key = settings.get_api_key("deepseek_api_key")
        self.base_url = "https://api.deepseek.com/v1"
        self.model = settings.translation.deepseek_model
        
    async def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text using DeepSeek API"""
        try:
            # Check cache first
            cache_key = f"deepseek_{hash(text)}_{source_lang}_{target_lang}"
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Using cached DeepSeek translation")
                return TranslationResult(**cached_result)
            
            # Prepare API request
            prompt = self._build_translation_prompt(text, source_lang, target_lang)
            
            # Call DeepSeek API
            result = await self._call_deepseek_api(prompt)
            
            # Cache result
            cache_manager.put(cache_key, result.__dict__, ttl=3600)  # 1 hour cache
            
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"service": "deepseek", "source_lang": source_lang, "target_lang": target_lang},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _build_translation_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """Build translation prompt for DeepSeek"""
        lang_names = {
            "zh": "中文",
            "en": "英语", 
            "ja": "日语",
            "ko": "韩语",
            "fr": "法语",
            "de": "德语",
            "es": "西班牙语",
            "ru": "俄语"
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        prompt = f"""请将以下{source_name}文本翻译为{target_name}。要求：
1. 保持原文的语气和情感
2. 确保翻译自然流畅
3. 如果是电影对话，要符合角色说话风格
4. 只返回翻译结果，不要添加解释

原文：
{text}

翻译："""
        
        return prompt
    
    async def _call_deepseek_api(self, prompt: str) -> TranslationResult:
        """Call DeepSeek translation API"""
        try:
            import requests
            
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.3,
                "top_p": 0.9
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result_data = response.json()
            
            if "error" in result_data:
                raise RuntimeError(f"DeepSeek API error: {result_data['error']}")
            
            # Extract translation
            translated_text = result_data["choices"][0]["message"]["content"].strip()
            
            # Calculate confidence (based on model response)
            confidence = min(0.9, len(translated_text) / max(len(prompt), 1))
            
            return TranslationResult(
                original_text=prompt.split("原文：")[1].split("翻译：")[0].strip(),
                translated_text=translated_text,
                source_lang="auto",  # Will be set by caller
                target_lang="auto",  # Will be set by caller
                confidence=confidence
            )
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "call_deepseek_api"},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise


class GLMTranslation:
    """GLM-4.5 translation service"""
    
    def __init__(self):
        self.api_key = settings.get_api_key("glm_api_key")
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model = settings.translation.glm_model
        
    async def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text using GLM API"""
        try:
            # Check cache first
            cache_key = f"glm_{hash(text)}_{source_lang}_{target_lang}"
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Using cached GLM translation")
                return TranslationResult(**cached_result)
            
            # Prepare API request
            prompt = self._build_translation_prompt(text, source_lang, target_lang)
            
            # Call GLM API
            result = await self._call_glm_api(prompt)
            
            # Cache result
            cache_manager.put(cache_key, result.__dict__, ttl=3600)
            
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"service": "glm", "source_lang": source_lang, "target_lang": target_lang},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    def _build_translation_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """Build translation prompt for GLM"""
        lang_names = {
            "zh": "中文",
            "en": "英语",
            "ja": "日语", 
            "ko": "韩语",
            "fr": "法语",
            "de": "德语",
            "es": "西班牙语",
            "ru": "俄语"
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        prompt = f"""你是一个专业的翻译助手。请将以下{source_name}文本翻译为{target_name}。

翻译要求：
- 保持原文的语调和情感色彩
- 确保翻译结果自然流畅，符合目标语言的表达习惯
- 如果是电影或电视剧的对话，要注意角色说话的风格和语境
- 只返回翻译结果，不要添加额外说明

原文：{text}

翻译："""
        
        return prompt
    
    async def _call_glm_api(self, prompt: str) -> TranslationResult:
        """Call GLM translation API"""
        try:
            import requests
            
            url = self.base_url
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.3,
                "top_p": 0.9
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result_data = response.json()
            
            if "error" in result_data:
                raise RuntimeError(f"GLM API error: {result_data['error']}")
            
            # Extract translation
            translated_text = result_data["choices"][0]["message"]["content"].strip()
            
            # Calculate confidence
            confidence = min(0.9, len(translated_text) / max(len(prompt), 1))
            
            return TranslationResult(
                original_text=prompt.split("原文：")[1].split("\n\n翻译：")[0].strip(),
                translated_text=translated_text,
                source_lang="auto",  # Will be set by caller
                target_lang="auto",  # Will be set by caller
                confidence=confidence
            )
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "call_glm_api"},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise


class TranslationService:
    """Main translation service"""
    
    def __init__(self):
        self.deepseek_service = DeepSeekTranslation()
        self.glm_service = GLMTranslation()
        self.primary_service = settings.translation.primary_service
        
    async def _initialize(self):
        """Initialize the service"""
        logger.info("Translation service initialized")
        return True
        
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text using primary service"""
        try:
            if not text.strip():
                return TranslationResult(text, text, source_lang, target_lang, 1.0)
            
            # Normalize language codes
            source_lang = self._normalize_language_code(source_lang)
            target_lang = self._normalize_language_code(target_lang)
            
            # Use primary service
            if self.primary_service == "deepseek":
                result = await self.deepseek_service.translate(text, source_lang, target_lang)
            elif self.primary_service == "glm":
                result = await self.glm_service.translate(text, source_lang, target_lang)
            else:
                raise ValueError(f"Unsupported primary service: {self.primary_service}")
            
            # Set language codes
            result.source_lang = source_lang
            result.target_lang = target_lang
            
            logger.info(f"Translation completed: {text[:30]}... -> {result.translated_text[:30]}...")
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"text": text[:50], "source_lang": source_lang, "target_lang": target_lang},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
        # Language mapping
    language_codes = {
            "chinese": "zh",
            "english": "en",
            "japanese": "ja",
            "korean": "ko",
            "french": "fr",
            "german": "de",
            "spanish": "es",
            "russian": "ru"
        }
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text using primary service"""
        try:
            if not text.strip():
                return TranslationResult(text, text, source_lang, target_lang, 1.0)
            
            # Normalize language codes
            source_lang = self._normalize_language_code(source_lang)
            target_lang = self._normalize_language_code(target_lang)
            
            # Use primary service
            if self.primary_service == "deepseek":
                result = await self.deepseek_service.translate(text, source_lang, target_lang)
            elif self.primary_service == "glm":
                result = await self.glm_service.translate(text, source_lang, target_lang)
            else:
                raise ValueError(f"Unsupported primary service: {self.primary_service}")
            
            # Set language codes
            result.source_lang = source_lang
            result.target_lang = target_lang
            
            logger.info(f"Translation completed: {text[:30]}... -> {result.translated_text[:30]}...")
            return result
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"text": text[:50], "source_lang": source_lang, "target_lang": target_lang},
                category=ErrorCategory.API,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def translate_segments(self, audio_analysis: AudioAnalysisResult, 
                               target_lang: str) -> AudioAnalysisResult:
        """Translate all audio segments"""
        try:
            logger.info(f"Starting translation for {len(audio_analysis.segments)} segments to {target_lang}")
            
            # Detect source language
            source_lang = self._detect_source_language(audio_analysis)
            
            # Translate segments in batches
            translated_segments = []
            batch_size = settings.translation.batch_size
            
            for i in range(0, len(audio_analysis.segments), batch_size):
                batch = audio_analysis.segments[i:i + batch_size]
                
                # Process batch asynchronously
                tasks = []
                for segment in batch:
                    if segment.text:
                        task = self._translate_segment(segment, source_lang, target_lang)
                        tasks.append(task)
                    else:
                        # Skip segments without text
                        translated_segments.append(segment)
                
                if tasks:
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Handle results
                    for result in batch_results:
                        if isinstance(result, Exception):
                            logger.error(f"Translation error: {result}")
                            # Keep original segment if translation fails
                            translated_segments.append(segment)
                        else:
                            translated_segments.append(result)
                
                # Update progress
                progress = min((i + len(batch)) / len(audio_analysis.segments), 1.0)
                logger.info(f"Translation progress: {progress:.2%}")
            
            # Update analysis result
            audio_analysis.segments = translated_segments
            
            logger.info("Translation completed for all segments")
            return audio_analysis
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"target_lang": target_lang, "segment_count": len(audio_analysis.segments)},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.HIGH
            )
            raise
    
    async def _translate_segment(self, segment: AudioSegment, source_lang: str, 
                               target_lang: str) -> AudioSegment:
        """Translate a single segment"""
        try:
            if not segment.text:
                return segment
            
            # Translate text
            result = await self.translate_text(segment.text, source_lang, target_lang)
            
            # Create translated segment
            translated_segment = AudioSegment(
                id=f"{segment.id}_translated",
                start_time=segment.start_time,
                end_time=segment.end_time,
                duration=segment.duration,
                audio_data=segment.audio_data,
                sample_rate=segment.sample_rate,
                speaker_id=segment.speaker_id,
                text=result.translated_text,
                language=target_lang,
                confidence=result.confidence
            )
            
            return translated_segment
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"segment_id": segment.id},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return segment
    
    def _detect_source_language(self, audio_analysis: AudioAnalysisResult) -> str:
        """Detect source language from audio analysis"""
        try:
            # Use language detection from audio analysis
            if audio_analysis.language:
                return audio_analysis.language
            
            # Check segment languages
            for segment in audio_analysis.segments:
                if segment.language:
                    return segment.language
            
            # Default to Chinese if no language detected
            return settings.translation.default_source_language
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "detect_source_language"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return settings.translation.default_source_language
    
    def _normalize_language_code(self, lang_code: str) -> str:
        """Normalize language code"""
        try:
            # Convert to lowercase
            lang_code = lang_code.lower()
            
            # Map full names to codes
            if lang_code in self.language_codes:
                return self.language_codes[lang_code]
            
            # Return as-is if already a code
            return lang_code
            
        except Exception:
            return lang_code
    
    async def translate_subtitle_file(self, input_path: str, output_path: str, 
                                   source_lang: str, target_lang: str) -> bool:
        """Translate subtitle file"""
        try:
            # Read subtitle file
            subtitle_content = Path(input_path).read_text(encoding='utf-8')
            
            # Parse subtitle content
            subtitles = self._parse_subtitles(subtitle_content)
            
            # Translate subtitles
            translated_subtitles = []
            for subtitle in subtitles:
                translated_result = await self.translate_text(
                    subtitle['text'], source_lang, target_lang
                )
                translated_subtitles.append({
                    'index': subtitle['index'],
                    'start_time': subtitle['start_time'],
                    'end_time': subtitle['end_time'],
                    'text': translated_result.translated_text
                })
            
            # Write translated subtitle file
            self._write_subtitle_file(output_path, translated_subtitles)
            
            logger.info(f"Subtitle file translated: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"input_path": input_path, "output_path": output_path},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            return False
    
    def _parse_subtitles(self, content: str) -> List[Dict]:
        """Parse subtitle content"""
        try:
            subtitles = []
            blocks = content.strip().split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        index = int(lines[0])
                        time_line = lines[1]
                        text = '\n'.join(lines[2:])
                        
                        # Parse time line
                        start_time, end_time = self._parse_time_line(time_line)
                        
                        subtitles.append({
                            'index': index,
                            'start_time': start_time,
                            'end_time': end_time,
                            'text': text
                        })
                    except Exception:
                        continue
            
            return subtitles
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"operation": "parse_subtitles"},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
            return []
    
    def _parse_time_line(self, time_line: str) -> Tuple[float, float]:
        """Parse SRT time line"""
        try:
            # Format: 00:00:00,000 --> 00:00:00,000
            parts = time_line.split(' --> ')
            start_str = parts[0]
            end_str = parts[1]
            
            def parse_time(time_str: str) -> float:
                # Parse HH:MM:SS,mmm format
                time_str = time_str.replace(',', '.')
                h, m, s = time_str.split(':')
                return int(h) * 3600 + int(m) * 60 + float(s)
            
            return parse_time(start_str), parse_time(end_str)
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"time_line": time_line},
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.LOW
            )
            return 0.0, 0.0
    
    def _write_subtitle_file(self, output_path: str, subtitles: List[Dict]):
        """Write subtitle file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for subtitle in subtitles:
                    # Format time for SRT
                    start_time = self._format_srt_time(subtitle['start_time'])
                    end_time = self._format_srt_time(subtitle['end_time'])
                    
                    # Write subtitle entry
                    f.write(f"{subtitle['index']}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{subtitle['text']}\n\n")
                    
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context={"output_path": output_path},
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
            raise
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format time in seconds to SRT format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"


# Create singleton instance
translation_service = TranslationService()
"""
Multilingual Handler - Manages multilingual text processing and language detection
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

try:
    from langdetect import detect, detect_langs
except ImportError:
    detect = None
    detect_langs = None
    print("Warning: langdetect not installed. Install with: pip install langdetect")

logger = logging.getLogger(__name__)


class Language(str, Enum):
    CHINESE = "zh"
    ENGLISH = "en"
    JAPANESE = "ja"
    KOREAN = "ko"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class MultilingualHandler:
    """Handles multilingual text processing and language detection"""
    
    def __init__(self):
        self.language_patterns = self._load_language_patterns()
        self.language_names = {
            Language.CHINESE: {"zh": "中文", "en": "Chinese"},
            Language.ENGLISH: {"zh": "英文", "en": "English"},
            Language.JAPANESE: {"zh": "日文", "en": "Japanese"},
            Language.KOREAN: {"zh": "韩文", "en": "Korean"},
            Language.MIXED: {"zh": "混合语言", "en": "Mixed Languages"},
            Language.UNKNOWN: {"zh": "未知语言", "en": "Unknown Language"}
        }
        
        # Language-specific processing rules
        self.processing_rules = self._load_processing_rules()
    
    def _load_language_patterns(self) -> Dict[Language, str]:
        """Load regex patterns for language detection"""
        return {
            Language.CHINESE: r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]',
            Language.JAPANESE: r'[\u3040-\u309f\u30a0-\u30ff]',
            Language.KOREAN: r'[\uac00-\ud7af]',
            Language.ENGLISH: r'[a-zA-Z]'
        }
    
    def _load_processing_rules(self) -> Dict[Language, Dict]:
        """Load language-specific processing rules"""
        return {
            Language.CHINESE: {
                "sentence_endings": ["。", "！", "？", "…"],
                "pause_markers": ["，", "、", "；", "："],
                "number_reading": "chinese",
                "tone_markers": True,
                "word_segmentation": True
            },
            Language.ENGLISH: {
                "sentence_endings": [".", "!", "?", "..."],
                "pause_markers": [",", ";", ":"],
                "number_reading": "english",
                "tone_markers": False,
                "word_segmentation": False
            },
            Language.JAPANESE: {
                "sentence_endings": ["。", "！", "？"],
                "pause_markers": ["、", "，"],
                "number_reading": "japanese",
                "tone_markers": True,
                "word_segmentation": False
            },
            Language.KOREAN: {
                "sentence_endings": [".", "!", "?"],
                "pause_markers": [",", ";"],
                "number_reading": "korean",
                "tone_markers": False,
                "word_segmentation": False
            }
        }
    
    def detect_language(self, text: str) -> Tuple[Language, float]:
        """
        Detect the primary language of text
        
        Returns:
            Tuple of (language, confidence)
        """
        try:
            # Remove non-text characters for analysis
            clean_text = re.sub(r'[^\w\s\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]', '', text)
            
            if not clean_text.strip():
                return Language.UNKNOWN, 0.0
            
            # Count characters for each language
            language_counts = {}
            total_chars = 0
            
            for language, pattern in self.language_patterns.items():
                matches = re.findall(pattern, clean_text)
                count = len(matches)
                if count > 0:
                    language_counts[language] = count
                    total_chars += count
            
            if total_chars == 0:
                return Language.UNKNOWN, 0.0
            
            # Calculate percentages
            language_percentages = {
                lang: count / total_chars 
                for lang, count in language_counts.items()
            }
            
            # Determine primary language
            if not language_percentages:
                return Language.UNKNOWN, 0.0
            
            primary_lang = max(language_percentages, key=language_percentages.get)
            primary_confidence = language_percentages[primary_lang]
            
            # Check for mixed language
            significant_languages = [
                lang for lang, pct in language_percentages.items() 
                if pct > 0.2  # More than 20%
            ]
            
            if len(significant_languages) > 1:
                return Language.MIXED, primary_confidence
            
            # Use langdetect as fallback for better accuracy
            if detect and primary_confidence < 0.8:
                try:
                    detected = detect(clean_text)
                    if detected in ['zh-cn', 'zh-tw', 'zh']:
                        return Language.CHINESE, 0.9
                    elif detected == 'en':
                        return Language.ENGLISH, 0.9
                    elif detected == 'ja':
                        return Language.JAPANESE, 0.9
                    elif detected == 'ko':
                        return Language.KOREAN, 0.9
                except:
                    pass
            
            return primary_lang, primary_confidence
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return Language.UNKNOWN, 0.0
    
    def detect_all_languages(self, text: str) -> List[Tuple[Language, float]]:
        """Detect all languages present in text"""
        try:
            clean_text = re.sub(r'[^\w\s\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]', '', text)
            
            if not clean_text.strip():
                return [(Language.UNKNOWN, 0.0)]
            
            language_counts = {}
            total_chars = 0
            
            for language, pattern in self.language_patterns.items():
                matches = re.findall(pattern, clean_text)
                count = len(matches)
                if count > 0:
                    language_counts[language] = count
                    total_chars += count
            
            if total_chars == 0:
                return [(Language.UNKNOWN, 0.0)]
            
            # Calculate percentages and sort
            results = [
                (lang, count / total_chars)
                for lang, count in language_counts.items()
            ]
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Multi-language detection failed: {e}")
            return [(Language.UNKNOWN, 0.0)]
    
    def split_by_language(self, text: str) -> List[Tuple[str, Language]]:
        """Split text into segments by language"""
        try:
            segments = []
            current_segment = ""
            current_language = Language.UNKNOWN
            
            for char in text:
                char_language = self._detect_char_language(char)
                
                if char_language != current_language and current_segment:
                    # Save current segment
                    segments.append((current_segment.strip(), current_language))
                    current_segment = char
                    current_language = char_language
                else:
                    current_segment += char
                    if current_language == Language.UNKNOWN:
                        current_language = char_language
            
            # Add final segment
            if current_segment.strip():
                segments.append((current_segment.strip(), current_language))
            
            return segments
            
        except Exception as e:
            logger.error(f"Language splitting failed: {e}")
            return [(text, Language.UNKNOWN)]
    
    def _detect_char_language(self, char: str) -> Language:
        """Detect language of a single character"""
        for language, pattern in self.language_patterns.items():
            if re.match(pattern, char):
                return language
        return Language.UNKNOWN
    
    def normalize_text(self, text: str, target_language: Language) -> str:
        """Normalize text for specific language"""
        try:
            if target_language == Language.CHINESE:
                return self._normalize_chinese(text)
            elif target_language == Language.ENGLISH:
                return self._normalize_english(text)
            elif target_language == Language.JAPANESE:
                return self._normalize_japanese(text)
            elif target_language == Language.KOREAN:
                return self._normalize_korean(text)
            else:
                return text
                
        except Exception as e:
            logger.error(f"Text normalization failed: {e}")
            return text
    
    def _normalize_chinese(self, text: str) -> str:
        """Normalize Chinese text"""
        # Convert full-width characters to half-width
        text = text.replace('（', '(').replace('）', ')')
        text = text.replace('【', '[').replace('】', ']')
        text = text.replace('《', '<').replace('》', '>')
        
        # Normalize punctuation
        text = text.replace('，', ', ').replace('。', '. ')
        text = text.replace('！', '! ').replace('？', '? ')
        
        return text
    
    def _normalize_english(self, text: str) -> str:
        """Normalize English text"""
        # Fix spacing around punctuation
        text = re.sub(r'\s*([,.!?;:])\s*', r'\1 ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _normalize_japanese(self, text: str) -> str:
        """Normalize Japanese text"""
        # Basic Japanese normalization
        text = text.replace('。', '. ').replace('、', ', ')
        return text
    
    def _normalize_korean(self, text: str) -> str:
        """Normalize Korean text"""
        # Basic Korean normalization
        return text
    
    def get_language_name(self, language: Language, display_language: str = "en") -> str:
        """Get human-readable language name"""
        return self.language_names.get(language, {}).get(display_language, str(language))
    
    def is_mixed_language(self, text: str, threshold: float = 0.2) -> bool:
        """Check if text contains mixed languages"""
        languages = self.detect_all_languages(text)
        significant_languages = [lang for lang, conf in languages if conf > threshold]
        return len(significant_languages) > 1
    
    def get_processing_rules(self, language: Language) -> Dict:
        """Get processing rules for specific language"""
        return self.processing_rules.get(language, self.processing_rules[Language.ENGLISH])
    
    def suggest_tts_language(self, text: str) -> str:
        """Suggest TTS language code for text"""
        primary_language, confidence = self.detect_language(text)
        
        # Map to TTS language codes
        tts_language_map = {
            Language.CHINESE: "zh-cn",
            Language.ENGLISH: "en",
            Language.JAPANESE: "ja",
            Language.KOREAN: "ko"
        }
        
        if confidence > 0.7:
            return tts_language_map.get(primary_language, "en")
        else:
            # Default to auto-detection
            return "auto"
    
    def prepare_for_tts(self, text: str, target_language: Optional[Language] = None) -> str:
        """Prepare text for TTS synthesis"""
        try:
            # Detect language if not specified
            if target_language is None:
                target_language, _ = self.detect_language(text)
            
            # Normalize text
            normalized_text = self.normalize_text(text, target_language)
            
            # Apply language-specific processing
            rules = self.get_processing_rules(target_language)
            
            # Add appropriate pauses
            for ending in rules["sentence_endings"]:
                normalized_text = normalized_text.replace(ending, f"{ending} ")
            
            for pause in rules["pause_markers"]:
                normalized_text = normalized_text.replace(pause, f"{pause} ")
            
            # Clean up extra spaces
            normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
            
            return normalized_text
            
        except Exception as e:
            logger.error(f"TTS preparation failed: {e}")
            return text
    
    def analyze_text_complexity(self, text: str) -> Dict[str, any]:
        """Analyze text complexity for different languages"""
        try:
            languages = self.detect_all_languages(text)
            primary_language, primary_confidence = self.detect_language(text)
            
            analysis = {
                "primary_language": primary_language,
                "primary_confidence": primary_confidence,
                "all_languages": languages,
                "is_mixed": self.is_mixed_language(text),
                "character_count": len(text),
                "word_count": len(text.split()),
                "complexity": "simple"
            }
            
            # Determine complexity
            if len(languages) > 2:
                analysis["complexity"] = "complex"
            elif analysis["is_mixed"]:
                analysis["complexity"] = "moderate"
            elif primary_confidence < 0.5:
                analysis["complexity"] = "moderate"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Text complexity analysis failed: {e}")
            return {"complexity": "unknown"}

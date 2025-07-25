"""
Text Processor - Handles text preprocessing for TTS
"""
import re
import logging
from typing import List, Dict, Optional, Tuple

try:
    import jieba
except ImportError:
    jieba = None
    print("Warning: jieba not installed. Install with: pip install jieba")

try:
    from opencc import OpenCC
except ImportError:
    OpenCC = None
    print("Warning: opencc not installed. Install with: pip install opencc-python-reimplemented")

try:
    import emoji
except ImportError:
    emoji = None
    print("Warning: emoji not installed. Install with: pip install emoji")

logger = logging.getLogger(__name__)


class TextProcessor:
    """Text preprocessing for multilingual TTS"""
    
    def __init__(self):
        self.chinese_converter = None
        self.emoji_enabled = emoji is not None
        
        # Initialize Chinese converter
        if OpenCC:
            try:
                self.chinese_converter = OpenCC('t2s')  # Traditional to Simplified
            except Exception as e:
                logger.warning(f"Failed to initialize Chinese converter: {e}")
        
        # Common text replacements
        self.replacements = {
            # Numbers
            "0": "零", "1": "一", "2": "二", "3": "三", "4": "四",
            "5": "五", "6": "六", "7": "七", "8": "八", "9": "九",
            
            # English numbers
            "zero": "零", "one": "一", "two": "二", "three": "三",
            "four": "四", "five": "五", "six": "六", "seven": "七",
            "eight": "八", "nine": "九", "ten": "十",
            
            # Common symbols
            "&": "和", "@": "at", "#": "井号", "%": "百分号",
            "+": "加", "-": "减", "=": "等于", "*": "乘",
            "/": "除", "\\": "反斜杠",
            
            # Punctuation for speech
            "...": "，", "…": "，", "--": "，",
            "!!": "！", "??": "？", "!?": "！？",
        }
        
        # Emotion markers
        self.emotion_markers = {
            "happy": ["😊", "😄", "😃", "🥰", "😍", "🤗"],
            "sad": ["😢", "😭", "😞", "😔", "💔"],
            "excited": ["🤩", "😆", "🎉", "🔥", "⚡"],
            "love": ["❤️", "💕", "💖", "💗", "😘"],
            "surprised": ["😲", "😮", "🤯", "😱"],
            "sleepy": ["😴", "💤", "😪", "🥱"],
        }
    
    def process_text(self, text: str, language: str = "auto") -> str:
        """Main text processing pipeline"""
        try:
            # Basic cleaning
            processed_text = self._clean_text(text)
            
            # Handle emojis
            processed_text = self._process_emojis(processed_text)
            
            # Language-specific processing
            if language == "zh" or self._is_chinese(processed_text):
                processed_text = self._process_chinese(processed_text)
            elif language == "en" or self._is_english(processed_text):
                processed_text = self._process_english(processed_text)
            else:
                # Auto-detect and process
                if self._is_chinese(processed_text):
                    processed_text = self._process_chinese(processed_text)
                else:
                    processed_text = self._process_english(processed_text)
            
            # Final cleanup
            processed_text = self._final_cleanup(processed_text)
            
            return processed_text
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return text  # Return original text if processing fails
    
    def _clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!!', text)
        text = re.sub(r'[?]{2,}', '??', text)
        
        return text
    
    def _process_emojis(self, text: str) -> str:
        """Process emojis in text"""
        if not self.emoji_enabled:
            # Simple emoji removal if emoji library not available
            return re.sub(r'[^\w\s\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff.,!?;:()[\]{}"\'-]', '', text)
        
        try:
            # Convert emojis to text descriptions
            def emoji_to_text(match):
                emoji_char = match.group()
                # Get emoji description
                description = emoji.demojize(emoji_char, delimiters=("", ""))
                
                # Map to emotion if possible
                for emotion, emoji_list in self.emotion_markers.items():
                    if emoji_char in emoji_list:
                        return f" *{emotion}* "
                
                # Return description or remove
                if description != emoji_char:
                    return f" {description} "
                else:
                    return " "
            
            # Replace emojis
            text = emoji.replace_emoji(text, replace=emoji_to_text)
            
            return text
            
        except Exception as e:
            logger.error(f"Emoji processing failed: {e}")
            return text
    
    def _process_chinese(self, text: str) -> str:
        """Process Chinese text"""
        try:
            # Convert traditional to simplified
            if self.chinese_converter:
                text = self.chinese_converter.convert(text)
            
            # Handle Chinese numbers and symbols
            for old, new in self.replacements.items():
                text = text.replace(old, new)
            
            # Add pauses for better speech rhythm
            text = re.sub(r'([。！？])', r'\1 ', text)
            text = re.sub(r'([，、；：])', r'\1', text)
            
            # Handle Chinese-specific patterns
            text = re.sub(r'(\d+)', self._number_to_chinese, text)
            
            return text
            
        except Exception as e:
            logger.error(f"Chinese processing failed: {e}")
            return text
    
    def _process_english(self, text: str) -> str:
        """Process English text"""
        try:
            # Expand contractions
            contractions = {
                "won't": "will not", "can't": "cannot", "n't": " not",
                "'re": " are", "'ve": " have", "'ll": " will",
                "'d": " would", "'m": " am", "'s": " is"
            }
            
            for contraction, expansion in contractions.items():
                text = text.replace(contraction, expansion)
            
            # Handle abbreviations
            abbreviations = {
                "Mr.": "Mister", "Mrs.": "Missus", "Dr.": "Doctor",
                "Prof.": "Professor", "vs.": "versus", "etc.": "etcetera",
                "i.e.": "that is", "e.g.": "for example"
            }
            
            for abbr, full in abbreviations.items():
                text = text.replace(abbr, full)
            
            # Add pauses for better speech rhythm
            text = re.sub(r'([.!?])', r'\1 ', text)
            text = re.sub(r'([,;:])', r'\1', text)
            
            return text
            
        except Exception as e:
            logger.error(f"English processing failed: {e}")
            return text
    
    def _number_to_chinese(self, match) -> str:
        """Convert numbers to Chinese"""
        try:
            number = match.group()
            if len(number) <= 2:  # Simple numbers
                chinese_digits = "零一二三四五六七八九"
                result = ""
                for digit in number:
                    result += chinese_digits[int(digit)]
                return result
            else:
                return number  # Keep complex numbers as is
        except:
            return match.group()
    
    def _is_chinese(self, text: str) -> bool:
        """Check if text is primarily Chinese"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u4e00-\u9fff]', text))
        return total_chars > 0 and chinese_chars / total_chars > 0.5
    
    def _is_english(self, text: str) -> bool:
        """Check if text is primarily English"""
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u4e00-\u9fff]', text))
        return total_chars > 0 and english_chars / total_chars > 0.5
    
    def _final_cleanup(self, text: str) -> str:
        """Final text cleanup"""
        # Remove excessive spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper punctuation spacing
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)
        
        # Remove leading/trailing spaces
        text = text.strip()
        
        # Ensure text ends with punctuation for better speech
        if text and text[-1] not in '.!?。！？':
            if self._is_chinese(text):
                text += '。'
            else:
                text += '.'
        
        return text
    
    def extract_emotions(self, text: str) -> List[str]:
        """Extract emotion indicators from text"""
        emotions = []
        
        # Check for emotion markers
        for emotion, markers in self.emotion_markers.items():
            for marker in markers:
                if marker in text:
                    emotions.append(emotion)
                    break
        
        # Check for emotion words
        emotion_words = {
            "happy": ["开心", "高兴", "快乐", "happy", "joy", "glad"],
            "sad": ["伤心", "难过", "悲伤", "sad", "sorrow", "upset"],
            "excited": ["兴奋", "激动", "excited", "thrilled"],
            "angry": ["生气", "愤怒", "angry", "mad"],
            "surprised": ["惊讶", "震惊", "surprised", "shocked"],
            "calm": ["平静", "冷静", "calm", "peaceful"],
        }
        
        text_lower = text.lower()
        for emotion, words in emotion_words.items():
            for word in words:
                if word in text_lower:
                    emotions.append(emotion)
                    break
        
        return list(set(emotions))  # Remove duplicates
    
    def segment_chinese(self, text: str) -> List[str]:
        """Segment Chinese text using jieba"""
        if jieba and self._is_chinese(text):
            try:
                return list(jieba.cut(text))
            except Exception as e:
                logger.error(f"Chinese segmentation failed: {e}")
        
        return text.split()
    
    def add_speech_marks(self, text: str, style: str = "normal") -> str:
        """Add speech marks for different speaking styles"""
        if style == "whisper":
            # Add whisper indicators
            text = f"*whisper* {text}"
        elif style == "excited":
            # Add excitement
            text = text.replace("!", "!!")
            text = text.replace("。", "！")
        elif style == "slow":
            # Add pauses
            text = text.replace(" ", "... ")
            text = text.replace("，", "，... ")
        
        return text

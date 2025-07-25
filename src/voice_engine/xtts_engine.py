"""
XTTS-v2 Engine for high-quality multilingual voice synthesis
"""
import os
import torch
import torchaudio
import numpy as np
from typing import Optional, Dict, Any, Union
from pathlib import Path
import logging

try:
    from TTS.api import TTS
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
except ImportError:
    TTS = None
    print("Warning: TTS library not installed. Install with: pip install TTS")

from ..config import settings, VoiceProfile

logger = logging.getLogger(__name__)


class XTTSEngine:
    """XTTS-v2 Text-to-Speech Engine"""
    
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        self.model_name = model_name
        self.model = None
        self.config = None
        self.device = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"
        self.sample_rate = 22050
        self.is_loaded = False
        
        # Supported languages for XTTS-v2
        self.supported_languages = [
            "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", 
            "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"
        ]
        
    def load_model(self) -> bool:
        """Load XTTS-v2 model"""
        try:
            if TTS is None:
                logger.error("TTS library not available")
                return False
                
            logger.info(f"Loading XTTS-v2 model on {self.device}")
            
            # Initialize TTS with XTTS-v2
            self.model = TTS(self.model_name).to(self.device)
            self.is_loaded = True
            
            logger.info("XTTS-v2 model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load XTTS-v2 model: {e}")
            return False
    
    def clone_voice(self, speaker_wav_path: str, output_path: str = None) -> bool:
        """Clone voice from audio sample"""
        try:
            if not self.is_loaded:
                if not self.load_model():
                    return False
            
            if not os.path.exists(speaker_wav_path):
                logger.error(f"Speaker audio file not found: {speaker_wav_path}")
                return False
            
            # Voice cloning is handled automatically by XTTS-v2
            # when providing speaker_wav parameter
            logger.info(f"Voice cloning prepared for: {speaker_wav_path}")
            return True
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return False
    
    def synthesize(
        self,
        text: str,
        language: str = "auto",
        speaker_wav: Optional[str] = None,
        voice_profile: Optional[VoiceProfile] = None,
        **kwargs
    ) -> Optional[np.ndarray]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            language: Language code (auto-detect if "auto")
            speaker_wav: Path to speaker audio for voice cloning
            voice_profile: Voice profile configuration
            **kwargs: Additional parameters
        
        Returns:
            Audio array or None if failed
        """
        try:
            if not self.is_loaded:
                if not self.load_model():
                    return None
            
            # Auto-detect language if needed
            if language == "auto":
                language = self._detect_language(text)
            
            # Map language codes
            language = self._map_language_code(language)
            
            if language not in self.supported_languages:
                logger.warning(f"Language {language} not supported, using English")
                language = "en"
            
            # Apply voice profile settings
            synthesis_kwargs = {}
            if voice_profile:
                synthesis_kwargs.update({
                    "speed": voice_profile.speed,
                    # Note: XTTS-v2 doesn't directly support pitch adjustment
                    # This would need post-processing
                })
            
            # Synthesize speech
            if speaker_wav and os.path.exists(speaker_wav):
                # Voice cloning mode
                wav = self.model.tts(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    **synthesis_kwargs
                )
            else:
                # Use default voice
                wav = self.model.tts(
                    text=text,
                    language=language,
                    **synthesis_kwargs
                )
            
            # Convert to numpy array if needed
            if isinstance(wav, torch.Tensor):
                wav = wav.cpu().numpy()
            
            # Apply voice profile modifications
            if voice_profile:
                wav = self._apply_voice_modifications(wav, voice_profile)
            
            return wav
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return None
    
    def synthesize_streaming(
        self,
        text: str,
        language: str = "auto",
        speaker_wav: Optional[str] = None,
        voice_profile: Optional[VoiceProfile] = None,
        chunk_size: int = 1024
    ):
        """
        Streaming synthesis (generator)
        
        Args:
            text: Text to synthesize
            language: Language code
            speaker_wav: Speaker audio path
            voice_profile: Voice profile
            chunk_size: Audio chunk size
        
        Yields:
            Audio chunks
        """
        try:
            # For now, synthesize full audio and chunk it
            # Future: Implement true streaming synthesis
            audio = self.synthesize(text, language, speaker_wav, voice_profile)
            
            if audio is not None:
                # Yield audio in chunks
                for i in range(0, len(audio), chunk_size):
                    yield audio[i:i + chunk_size]
                    
        except Exception as e:
            logger.error(f"Streaming synthesis failed: {e}")
            yield None
    
    def _detect_language(self, text: str) -> str:
        """Detect language from text"""
        try:
            from langdetect import detect
            detected = detect(text)
            
            # Map common language codes
            lang_map = {
                "zh": "zh-cn",
                "zh-cn": "zh-cn",
                "en": "en",
                "ja": "ja",
                "ko": "ko"
            }
            
            return lang_map.get(detected, "en")
            
        except Exception:
            # Default to English if detection fails
            return "en"
    
    def _map_language_code(self, language: str) -> str:
        """Map language codes to XTTS-v2 format"""
        lang_map = {
            "zh": "zh-cn",
            "chinese": "zh-cn",
            "english": "en",
            "japanese": "ja",
            "korean": "ko"
        }
        return lang_map.get(language.lower(), language)
    
    def _apply_voice_modifications(self, audio: np.ndarray, voice_profile: VoiceProfile) -> np.ndarray:
        """Apply voice profile modifications to audio"""
        try:
            # Apply pitch modification if needed
            if voice_profile.pitch != 1.0:
                # Simple pitch shifting using resampling
                # For better quality, consider using librosa.effects.pitch_shift
                target_length = int(len(audio) / voice_profile.pitch)
                audio = np.interp(
                    np.linspace(0, len(audio), target_length),
                    np.arange(len(audio)),
                    audio
                )
            
            # Speed is already handled in synthesis
            
            return audio
            
        except Exception as e:
            logger.error(f"Voice modification failed: {e}")
            return audio
    
    def get_available_speakers(self) -> list:
        """Get list of available speakers"""
        # XTTS-v2 uses voice cloning, so speakers are dynamic
        return ["cloned_voice"]
    
    def cleanup(self):
        """Cleanup resources"""
        if self.model:
            del self.model
            self.model = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_loaded = False

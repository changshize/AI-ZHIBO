"""
Voice Manager - Orchestrates multiple TTS engines and voice profiles
"""
import asyncio
import logging
from typing import Optional, Dict, Any, Generator, Union
import numpy as np
from enum import Enum

from .xtts_engine import XTTSEngine
from .chattts_engine import ChatTTSEngine
from .realtime_tts import RealtimeTTSEngine
from ..config import settings, VoiceProfile, VoiceEngine

logger = logging.getLogger(__name__)


class SynthesisMode(str, Enum):
    BATCH = "batch"
    STREAMING = "streaming"
    REALTIME = "realtime"


class VoiceManager:
    """
    Central voice management system that coordinates multiple TTS engines
    """
    
    def __init__(self):
        self.engines: Dict[str, Any] = {}
        self.current_engine = None
        self.fallback_engine = None
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.current_profile = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize voice engines"""
        try:
            logger.info("Initializing Voice Manager")
            
            # Initialize XTTS-v2 engine
            if settings.primary_voice_engine == VoiceEngine.XTTS_V2:
                xtts_engine = XTTSEngine()
                if xtts_engine.load_model():
                    self.engines[VoiceEngine.XTTS_V2] = xtts_engine
                    self.current_engine = xtts_engine
                    logger.info("XTTS-v2 engine initialized as primary")
                else:
                    logger.warning("Failed to initialize XTTS-v2 engine")

            # Initialize ChatTTS engine
            if settings.primary_voice_engine == VoiceEngine.CHATTTS or settings.fallback_voice_engine == VoiceEngine.CHATTTS:
                chattts_engine = ChatTTSEngine()
                if chattts_engine.load_model():
                    self.engines[VoiceEngine.CHATTTS] = chattts_engine
                    if settings.primary_voice_engine == VoiceEngine.CHATTTS:
                        self.current_engine = chattts_engine
                    logger.info("ChatTTS engine initialized")
                else:
                    logger.warning("Failed to initialize ChatTTS engine")

            # Initialize RealtimeTTS engine
            realtime_engine = RealtimeTTSEngine()
            if realtime_engine.initialize():
                self.engines[VoiceEngine.REALTIME_TTS] = realtime_engine
                if not self.current_engine:
                    self.current_engine = realtime_engine
                logger.info("RealtimeTTS engine initialized")
            else:
                logger.warning("Failed to initialize RealtimeTTS engine")
            
            # Set fallback engine
            if settings.fallback_voice_engine in self.engines:
                self.fallback_engine = self.engines[settings.fallback_voice_engine]
            
            # Load default voice profiles
            self._load_default_profiles()
            
            self.is_initialized = len(self.engines) > 0
            
            if self.is_initialized:
                logger.info(f"Voice Manager initialized with {len(self.engines)} engines")
            else:
                logger.error("No voice engines available")
            
            return self.is_initialized
            
        except Exception as e:
            logger.error(f"Voice Manager initialization failed: {e}")
            return False
    
    def synthesize(
        self,
        text: str,
        voice_profile_name: Optional[str] = None,
        language: str = "auto",
        mode: SynthesisMode = SynthesisMode.BATCH,
        **kwargs
    ) -> Union[np.ndarray, Generator[bytes, None, None], None]:
        """
        Synthesize speech with specified parameters
        
        Args:
            text: Text to synthesize
            voice_profile_name: Name of voice profile to use
            language: Language code
            mode: Synthesis mode (batch, streaming, realtime)
            **kwargs: Additional parameters
            
        Returns:
            Audio data (format depends on mode)
        """
        try:
            if not self.is_initialized:
                logger.error("Voice Manager not initialized")
                return None
            
            # Get voice profile
            voice_profile = self._get_voice_profile(voice_profile_name)
            
            # Select appropriate engine based on mode
            engine = self._select_engine(mode)
            if not engine:
                logger.error("No suitable engine available")
                return None
            
            # Synthesize based on mode
            if mode == SynthesisMode.BATCH:
                return self._synthesize_batch(engine, text, language, voice_profile, **kwargs)
            elif mode == SynthesisMode.STREAMING:
                return self._synthesize_streaming(engine, text, language, voice_profile, **kwargs)
            elif mode == SynthesisMode.REALTIME:
                return self._synthesize_realtime(engine, text, language, voice_profile, **kwargs)
            else:
                logger.error(f"Unknown synthesis mode: {mode}")
                return None
                
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return self._try_fallback(text, voice_profile_name, language, mode, **kwargs)
    
    def _synthesize_batch(
        self,
        engine,
        text: str,
        language: str,
        voice_profile: Optional[VoiceProfile],
        **kwargs
    ) -> Optional[np.ndarray]:
        """Batch synthesis"""
        try:
            if hasattr(engine, 'synthesize'):
                speaker_wav = voice_profile.voice_sample_path if voice_profile else None
                return engine.synthesize(
                    text=text,
                    language=language,
                    speaker_wav=speaker_wav,
                    voice_profile=voice_profile,
                    **kwargs
                )
            else:
                logger.error("Engine doesn't support batch synthesis")
                return None
                
        except Exception as e:
            logger.error(f"Batch synthesis failed: {e}")
            return None
    
    def _synthesize_streaming(
        self,
        engine,
        text: str,
        language: str,
        voice_profile: Optional[VoiceProfile],
        **kwargs
    ) -> Optional[Generator[bytes, None, None]]:
        """Streaming synthesis"""
        try:
            if hasattr(engine, 'synthesize_streaming'):
                return engine.synthesize_streaming(
                    text=text,
                    language=language,
                    voice_profile=voice_profile,
                    **kwargs
                )
            elif hasattr(engine, 'synthesize'):
                # Fallback: convert batch to streaming
                audio = engine.synthesize(
                    text=text,
                    language=language,
                    speaker_wav=voice_profile.voice_sample_path if voice_profile else None,
                    voice_profile=voice_profile,
                    **kwargs
                )
                if audio is not None:
                    return self._convert_to_streaming(audio)
            
            logger.error("Engine doesn't support streaming synthesis")
            return None
            
        except Exception as e:
            logger.error(f"Streaming synthesis failed: {e}")
            return None
    
    def _synthesize_realtime(
        self,
        engine,
        text: str,
        language: str,
        voice_profile: Optional[VoiceProfile],
        **kwargs
    ) -> Optional[Generator[bytes, None, None]]:
        """Real-time synthesis"""
        try:
            # Prefer RealtimeTTS for real-time mode
            if VoiceEngine.REALTIME_TTS in self.engines:
                realtime_engine = self.engines[VoiceEngine.REALTIME_TTS]
                return realtime_engine.synthesize_streaming(
                    text=text,
                    voice_profile=voice_profile,
                    language=language
                )
            else:
                # Fallback to streaming mode
                return self._synthesize_streaming(engine, text, language, voice_profile, **kwargs)
                
        except Exception as e:
            logger.error(f"Real-time synthesis failed: {e}")
            return None
    
    def _convert_to_streaming(self, audio: np.ndarray, chunk_size: int = 1024) -> Generator[bytes, None, None]:
        """Convert batch audio to streaming chunks"""
        try:
            # Convert to int16 and bytes
            audio_int16 = (audio * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()
            
            # Yield in chunks
            for i in range(0, len(audio_bytes), chunk_size * 2):  # *2 for int16
                yield audio_bytes[i:i + chunk_size * 2]
                
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
    
    def _select_engine(self, mode: SynthesisMode):
        """Select appropriate engine for synthesis mode"""
        if mode == SynthesisMode.REALTIME and VoiceEngine.REALTIME_TTS in self.engines:
            return self.engines[VoiceEngine.REALTIME_TTS]
        elif mode in [SynthesisMode.BATCH, SynthesisMode.STREAMING] and self.current_engine:
            return self.current_engine
        elif self.engines:
            # Return any available engine
            return next(iter(self.engines.values()))
        else:
            return None
    
    def _try_fallback(self, text: str, voice_profile_name: Optional[str], language: str, mode: SynthesisMode, **kwargs):
        """Try fallback engine if primary fails"""
        try:
            if self.fallback_engine and self.fallback_engine != self.current_engine:
                logger.info("Trying fallback engine")
                voice_profile = self._get_voice_profile(voice_profile_name)
                
                if mode == SynthesisMode.BATCH:
                    return self._synthesize_batch(self.fallback_engine, text, language, voice_profile, **kwargs)
                elif mode == SynthesisMode.STREAMING:
                    return self._synthesize_streaming(self.fallback_engine, text, language, voice_profile, **kwargs)
                elif mode == SynthesisMode.REALTIME:
                    return self._synthesize_realtime(self.fallback_engine, text, language, voice_profile, **kwargs)
            
            return None
            
        except Exception as e:
            logger.error(f"Fallback synthesis failed: {e}")
            return None
    
    def _get_voice_profile(self, profile_name: Optional[str]) -> Optional[VoiceProfile]:
        """Get voice profile by name"""
        if profile_name and profile_name in self.voice_profiles:
            return self.voice_profiles[profile_name]
        elif self.current_profile:
            return self.current_profile
        elif self.voice_profiles:
            # Return first available profile
            return next(iter(self.voice_profiles.values()))
        else:
            return None
    
    def _load_default_profiles(self):
        """Load default voice profiles"""
        # Default female young voice profiles
        self.voice_profiles["cute_girl"] = VoiceProfile(
            name="cute_girl",
            gender="female",
            age_range="young",
            language="auto",
            pitch=1.2,
            speed=1.0,
            emotion="cheerful"
        )
        
        self.voice_profiles["asmr_girl"] = VoiceProfile(
            name="asmr_girl",
            gender="female",
            age_range="young",
            language="auto",
            pitch=0.9,
            speed=0.8,
            emotion="calm"
        )
        
        self.voice_profiles["energetic_girl"] = VoiceProfile(
            name="energetic_girl",
            gender="female",
            age_range="young",
            language="auto",
            pitch=1.3,
            speed=1.2,
            emotion="excited"
        )
        
        # Set default profile
        self.current_profile = self.voice_profiles["cute_girl"]
        
        logger.info(f"Loaded {len(self.voice_profiles)} default voice profiles")
    
    def add_voice_profile(self, profile: VoiceProfile) -> bool:
        """Add a new voice profile"""
        try:
            self.voice_profiles[profile.name] = profile
            logger.info(f"Added voice profile: {profile.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add voice profile: {e}")
            return False
    
    def set_current_profile(self, profile_name: str) -> bool:
        """Set current voice profile"""
        if profile_name in self.voice_profiles:
            self.current_profile = self.voice_profiles[profile_name]
            logger.info(f"Switched to voice profile: {profile_name}")
            return True
        else:
            logger.error(f"Voice profile not found: {profile_name}")
            return False
    
    def get_available_profiles(self) -> list:
        """Get list of available voice profiles"""
        return list(self.voice_profiles.keys())
    
    def get_available_engines(self) -> list:
        """Get list of available engines"""
        return list(self.engines.keys())
    
    def switch_engine(self, engine_name: str) -> bool:
        """Switch primary engine"""
        if engine_name in self.engines:
            self.current_engine = self.engines[engine_name]
            logger.info(f"Switched to engine: {engine_name}")
            return True
        else:
            logger.error(f"Engine not found: {engine_name}")
            return False
    
    def cleanup(self):
        """Cleanup all engines"""
        for engine in self.engines.values():
            if hasattr(engine, 'cleanup'):
                engine.cleanup()
        
        self.engines.clear()
        self.current_engine = None
        self.fallback_engine = None
        self.is_initialized = False
        
        logger.info("Voice Manager cleaned up")

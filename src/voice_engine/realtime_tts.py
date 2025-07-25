"""
RealtimeTTS Engine wrapper for streaming text-to-speech
"""
import asyncio
import threading
import queue
import numpy as np
from typing import Optional, Generator, Dict, Any
import logging

try:
    from RealtimeTTS import TextToAudioStream, CoquiEngine, SystemEngine
except ImportError:
    TextToAudioStream = None
    CoquiEngine = None
    SystemEngine = None
    print("Warning: RealtimeTTS not installed. Install with: pip install RealtimeTTS")

from ..config import settings, VoiceProfile

logger = logging.getLogger(__name__)


class RealtimeTTSEngine:
    """RealtimeTTS wrapper for streaming synthesis"""
    
    def __init__(self, engine_type: str = "coqui"):
        self.engine_type = engine_type
        self.stream = None
        self.engine = None
        self.is_initialized = False
        self.audio_queue = queue.Queue()
        self.is_streaming = False
        
    def initialize(self) -> bool:
        """Initialize RealtimeTTS engine"""
        try:
            if TextToAudioStream is None:
                logger.error("RealtimeTTS library not available")
                return False
            
            # Initialize the appropriate engine
            if self.engine_type == "coqui" and CoquiEngine:
                logger.info("Initializing Coqui engine for RealtimeTTS")
                self.engine = CoquiEngine()
            elif self.engine_type == "system" and SystemEngine:
                logger.info("Initializing System engine for RealtimeTTS")
                self.engine = SystemEngine()
            else:
                logger.error(f"Engine type {self.engine_type} not available")
                return False
            
            # Create the audio stream
            self.stream = TextToAudioStream(self.engine)
            self.is_initialized = True
            
            logger.info("RealtimeTTS engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RealtimeTTS: {e}")
            return False
    
    def synthesize_streaming(
        self,
        text: str,
        voice_profile: Optional[VoiceProfile] = None,
        language: str = "auto"
    ) -> Generator[bytes, None, None]:
        """
        Stream audio synthesis in real-time
        
        Args:
            text: Text to synthesize
            voice_profile: Voice configuration
            language: Language code
            
        Yields:
            Audio chunks as bytes
        """
        try:
            if not self.is_initialized:
                if not self.initialize():
                    return
            
            # Configure voice settings
            if voice_profile:
                self._apply_voice_settings(voice_profile)
            
            # Start streaming
            self.is_streaming = True
            
            # Feed text to the stream
            self.stream.feed(text)
            
            # Stream audio chunks
            for audio_chunk in self.stream.generator():
                if not self.is_streaming:
                    break
                
                # Convert to bytes if needed
                if isinstance(audio_chunk, np.ndarray):
                    audio_chunk = (audio_chunk * 32767).astype(np.int16).tobytes()
                
                yield audio_chunk
            
            # Signal end of stream
            self.stream.stop()
            
        except Exception as e:
            logger.error(f"Streaming synthesis failed: {e}")
        finally:
            self.is_streaming = False
    
    def synthesize_async(
        self,
        text: str,
        voice_profile: Optional[VoiceProfile] = None,
        language: str = "auto",
        callback=None
    ):
        """
        Asynchronous synthesis with callback
        
        Args:
            text: Text to synthesize
            voice_profile: Voice configuration
            language: Language code
            callback: Function to call with audio chunks
        """
        def synthesis_worker():
            try:
                for audio_chunk in self.synthesize_streaming(text, voice_profile, language):
                    if callback:
                        callback(audio_chunk)
                    else:
                        self.audio_queue.put(audio_chunk)
                        
                # Signal completion
                if callback:
                    callback(None)  # None indicates end of stream
                else:
                    self.audio_queue.put(None)
                    
            except Exception as e:
                logger.error(f"Async synthesis failed: {e}")
                if callback:
                    callback(None)
                else:
                    self.audio_queue.put(None)
        
        # Start synthesis in background thread
        thread = threading.Thread(target=synthesis_worker)
        thread.daemon = True
        thread.start()
    
    def get_audio_chunks(self) -> Generator[bytes, None, None]:
        """Get audio chunks from queue"""
        while True:
            try:
                chunk = self.audio_queue.get(timeout=1.0)
                if chunk is None:  # End of stream signal
                    break
                yield chunk
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error getting audio chunks: {e}")
                break
    
    def _apply_voice_settings(self, voice_profile: VoiceProfile):
        """Apply voice profile settings to the engine"""
        try:
            if not self.engine:
                return
            
            # Apply settings based on engine type
            if hasattr(self.engine, 'set_voice'):
                # For engines that support voice selection
                if voice_profile.voice_sample_path:
                    self.engine.set_voice(voice_profile.voice_sample_path)
            
            if hasattr(self.engine, 'set_speed'):
                self.engine.set_speed(voice_profile.speed)
            
            if hasattr(self.engine, 'set_pitch'):
                self.engine.set_pitch(voice_profile.pitch)
            
            logger.debug(f"Applied voice settings: {voice_profile.name}")
            
        except Exception as e:
            logger.error(f"Failed to apply voice settings: {e}")
    
    def stop_streaming(self):
        """Stop current streaming"""
        self.is_streaming = False
        if self.stream:
            try:
                self.stream.stop()
            except Exception as e:
                logger.error(f"Error stopping stream: {e}")
    
    def pause_streaming(self):
        """Pause streaming"""
        if self.stream:
            try:
                self.stream.pause()
            except Exception as e:
                logger.error(f"Error pausing stream: {e}")
    
    def resume_streaming(self):
        """Resume streaming"""
        if self.stream:
            try:
                self.stream.resume()
            except Exception as e:
                logger.error(f"Error resuming stream: {e}")
    
    def set_voice_clone(self, voice_sample_path: str) -> bool:
        """Set voice cloning sample"""
        try:
            if not self.engine:
                return False
            
            if hasattr(self.engine, 'clone_voice'):
                self.engine.clone_voice(voice_sample_path)
                logger.info(f"Voice cloned from: {voice_sample_path}")
                return True
            else:
                logger.warning("Voice cloning not supported by current engine")
                return False
                
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return False
    
    def get_supported_languages(self) -> list:
        """Get supported languages"""
        if self.engine and hasattr(self.engine, 'get_languages'):
            return self.engine.get_languages()
        return ["en", "zh"]  # Default fallback
    
    def get_available_voices(self) -> list:
        """Get available voices"""
        if self.engine and hasattr(self.engine, 'get_voices'):
            return self.engine.get_voices()
        return ["default"]  # Default fallback
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_streaming()
        
        if self.stream:
            try:
                self.stream.stop()
                del self.stream
            except Exception as e:
                logger.error(f"Error cleaning up stream: {e}")
            self.stream = None
        
        if self.engine:
            try:
                del self.engine
            except Exception as e:
                logger.error(f"Error cleaning up engine: {e}")
            self.engine = None
        
        self.is_initialized = False
        
        # Clear audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

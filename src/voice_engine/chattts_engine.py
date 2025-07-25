"""
ChatTTS Engine - Optimized for Chinese/English conversational speech
"""
import torch
import numpy as np
from typing import Optional, Dict, Any, Union, List
import logging
import os

try:
    import ChatTTS
except ImportError:
    ChatTTS = None
    print("Warning: ChatTTS not installed. Install with: pip install ChatTTS")

from ..config import settings, VoiceProfile

logger = logging.getLogger(__name__)


class ChatTTSEngine:
    """ChatTTS Text-to-Speech Engine optimized for conversation"""
    
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"
        self.sample_rate = 24000  # ChatTTS default sample rate
        self.is_loaded = False
        
        # ChatTTS specific settings
        self.spk_stat = None  # Speaker statistics
        self.spk_emb = None   # Speaker embedding
        
        # Supported languages
        self.supported_languages = ["zh", "en", "zh-cn", "en-us"]
        
        # Voice presets
        self.voice_presets = {
            "female_young": {"spk_emb": None, "temperature": 0.3},
            "female_mature": {"spk_emb": None, "temperature": 0.5},
            "male_young": {"spk_emb": None, "temperature": 0.4},
            "male_mature": {"spk_emb": None, "temperature": 0.6}
        }
    
    def load_model(self) -> bool:
        """Load ChatTTS model"""
        try:
            if ChatTTS is None:
                logger.error("ChatTTS library not available")
                return False
            
            logger.info(f"Loading ChatTTS model on {self.device}")
            
            # Initialize ChatTTS
            self.model = ChatTTS.Chat()
            
            # Load model with appropriate settings
            success = self.model.load_models(
                compile=False,  # Set to True for better performance if supported
                device=self.device
            )
            
            if not success:
                logger.error("Failed to load ChatTTS models")
                return False
            
            # Load speaker statistics
            self._load_speaker_presets()
            
            self.is_loaded = True
            logger.info("ChatTTS model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ChatTTS model: {e}")
            return False
    
    def _load_speaker_presets(self):
        """Load speaker presets and embeddings"""
        try:
            if not self.model:
                return
            
            # Sample speaker embeddings for different voice types
            # In practice, you would load pre-computed embeddings
            logger.info("Loading speaker presets...")
            
            # Generate random speaker embeddings as placeholders
            # In real implementation, use pre-trained speaker embeddings
            for preset_name in self.voice_presets.keys():
                # This is a placeholder - in real implementation,
                # you would load actual speaker embeddings
                self.voice_presets[preset_name]["spk_emb"] = self.model.sample_random_speaker()
            
            logger.info("Speaker presets loaded")
            
        except Exception as e:
            logger.error(f"Failed to load speaker presets: {e}")
    
    def synthesize(
        self,
        text: str,
        language: str = "auto",
        speaker_preset: str = "female_young",
        voice_profile: Optional[VoiceProfile] = None,
        **kwargs
    ) -> Optional[np.ndarray]:
        """
        Synthesize speech from text using ChatTTS
        
        Args:
            text: Text to synthesize
            language: Language code
            speaker_preset: Speaker preset name
            voice_profile: Voice profile configuration
            **kwargs: Additional parameters
        
        Returns:
            Audio array or None if failed
        """
        try:
            if not self.is_loaded:
                if not self.load_model():
                    return None
            
            # Prepare text
            processed_text = self._prepare_text(text, language)
            
            # Get speaker settings
            speaker_settings = self._get_speaker_settings(speaker_preset, voice_profile)
            
            # Prepare inference parameters
            params_infer_code = {
                'spk_emb': speaker_settings.get('spk_emb'),
                'temperature': speaker_settings.get('temperature', 0.3),
                'top_P': 0.7,
                'top_K': 20,
            }
            
            params_refine_text = {
                'prompt': '[oral_2][laugh_0][break_6]'
            }
            
            # Apply voice profile adjustments
            if voice_profile:
                params_infer_code.update(self._apply_voice_profile(voice_profile))
            
            # Synthesize
            logger.debug(f"Synthesizing with ChatTTS: {processed_text[:50]}...")
            
            wavs = self.model.infer(
                [processed_text],
                params_refine_text=params_refine_text,
                params_infer_code=params_infer_code,
                use_decoder=True
            )
            
            if wavs and len(wavs) > 0:
                # Convert to numpy array
                audio = wavs[0]
                if isinstance(audio, torch.Tensor):
                    audio = audio.cpu().numpy()
                
                # Apply post-processing
                audio = self._post_process_audio(audio, voice_profile)
                
                return audio
            else:
                logger.error("ChatTTS synthesis returned empty result")
                return None
                
        except Exception as e:
            logger.error(f"ChatTTS synthesis failed: {e}")
            return None
    
    def synthesize_streaming(
        self,
        text: str,
        language: str = "auto",
        speaker_preset: str = "female_young",
        voice_profile: Optional[VoiceProfile] = None,
        chunk_size: int = 1024
    ):
        """
        Streaming synthesis (generator)
        Note: ChatTTS doesn't natively support streaming, so we chunk the output
        """
        try:
            # Synthesize full audio first
            audio = self.synthesize(text, language, speaker_preset, voice_profile)
            
            if audio is not None:
                # Yield audio in chunks
                for i in range(0, len(audio), chunk_size):
                    yield audio[i:i + chunk_size]
            else:
                yield None
                
        except Exception as e:
            logger.error(f"ChatTTS streaming synthesis failed: {e}")
            yield None
    
    def _prepare_text(self, text: str, language: str) -> str:
        """Prepare text for ChatTTS synthesis"""
        try:
            # ChatTTS specific text preprocessing
            processed_text = text.strip()
            
            # Add language-specific markers if needed
            if language in ["zh", "zh-cn"] or self._is_chinese(text):
                # Chinese text processing
                processed_text = self._process_chinese_text(processed_text)
            elif language in ["en", "en-us"] or self._is_english(text):
                # English text processing
                processed_text = self._process_english_text(processed_text)
            
            # Add ChatTTS control tokens for better quality
            processed_text = f"[oral_2][laugh_0][break_4]{processed_text}"
            
            return processed_text
            
        except Exception as e:
            logger.error(f"Text preparation failed: {e}")
            return text
    
    def _process_chinese_text(self, text: str) -> str:
        """Process Chinese text for ChatTTS"""
        # Add pauses for better rhythm
        text = text.replace('，', '，[break_2]')
        text = text.replace('。', '。[break_4]')
        text = text.replace('！', '！[break_3]')
        text = text.replace('？', '？[break_3]')
        return text
    
    def _process_english_text(self, text: str) -> str:
        """Process English text for ChatTTS"""
        # Add pauses for better rhythm
        text = text.replace(',', ',[break_2]')
        text = text.replace('.', '.[break_4]')
        text = text.replace('!', '![break_3]')
        text = text.replace('?', '?[break_3]')
        return text
    
    def _is_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        import re
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u4e00-\u9fff]', text))
        return total_chars > 0 and chinese_chars / total_chars > 0.5
    
    def _is_english(self, text: str) -> bool:
        """Check if text contains English characters"""
        import re
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u4e00-\u9fff]', text))
        return total_chars > 0 and english_chars / total_chars > 0.5
    
    def _get_speaker_settings(self, preset: str, voice_profile: Optional[VoiceProfile]) -> Dict:
        """Get speaker settings for synthesis"""
        settings = self.voice_presets.get(preset, self.voice_presets["female_young"]).copy()
        
        # Apply voice profile modifications
        if voice_profile:
            # Adjust temperature based on emotion
            emotion_temp_map = {
                "excited": 0.8,
                "happy": 0.6,
                "calm": 0.3,
                "sad": 0.2,
                "angry": 0.7
            }
            
            if voice_profile.emotion in emotion_temp_map:
                settings["temperature"] = emotion_temp_map[voice_profile.emotion]
        
        return settings
    
    def _apply_voice_profile(self, voice_profile: VoiceProfile) -> Dict:
        """Apply voice profile settings to inference parameters"""
        adjustments = {}
        
        # Map voice profile to ChatTTS parameters
        if voice_profile.speed != 1.0:
            # ChatTTS doesn't directly support speed adjustment
            # This would need post-processing
            pass
        
        if voice_profile.pitch != 1.0:
            # ChatTTS doesn't directly support pitch adjustment
            # This would need post-processing
            pass
        
        return adjustments
    
    def _post_process_audio(self, audio: np.ndarray, voice_profile: Optional[VoiceProfile]) -> np.ndarray:
        """Post-process audio based on voice profile"""
        try:
            if not voice_profile:
                return audio
            
            # Apply speed adjustment
            if voice_profile.speed != 1.0:
                # Simple speed adjustment by resampling
                target_length = int(len(audio) / voice_profile.speed)
                audio = np.interp(
                    np.linspace(0, len(audio), target_length),
                    np.arange(len(audio)),
                    audio
                )
            
            # Apply pitch adjustment (basic implementation)
            if voice_profile.pitch != 1.0:
                # This is a very basic pitch shift
                # For better quality, use librosa.effects.pitch_shift
                target_length = int(len(audio) / voice_profile.pitch)
                audio = np.interp(
                    np.linspace(0, len(audio), target_length),
                    np.arange(len(audio)),
                    audio
                )
            
            return audio
            
        except Exception as e:
            logger.error(f"Audio post-processing failed: {e}")
            return audio
    
    def get_available_speakers(self) -> List[str]:
        """Get list of available speaker presets"""
        return list(self.voice_presets.keys())
    
    def add_speaker_preset(self, name: str, spk_emb: Any, temperature: float = 0.3) -> bool:
        """Add custom speaker preset"""
        try:
            self.voice_presets[name] = {
                "spk_emb": spk_emb,
                "temperature": temperature
            }
            logger.info(f"Added speaker preset: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add speaker preset: {e}")
            return False
    
    def save_speaker_preset(self, name: str, file_path: str) -> bool:
        """Save speaker preset to file"""
        try:
            if name not in self.voice_presets:
                logger.error(f"Speaker preset not found: {name}")
                return False
            
            preset = self.voice_presets[name]
            torch.save(preset, file_path)
            logger.info(f"Speaker preset saved: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save speaker preset: {e}")
            return False
    
    def load_speaker_preset(self, name: str, file_path: str) -> bool:
        """Load speaker preset from file"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"Preset file not found: {file_path}")
                return False
            
            preset = torch.load(file_path, map_location=self.device)
            self.voice_presets[name] = preset
            logger.info(f"Speaker preset loaded: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load speaker preset: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.model:
            del self.model
            self.model = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_loaded = False
        logger.info("ChatTTS engine cleaned up")

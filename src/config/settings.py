"""
Configuration settings for AI Voice Streaming Host
"""
import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
from enum import Enum


class VoiceEngine(str, Enum):
    XTTS_V2 = "xtts_v2"
    CHATTTS = "chattts"
    REALTIME_TTS = "realtime_tts"


class Language(str, Enum):
    CHINESE = "zh"
    ENGLISH = "en"
    AUTO = "auto"


class StreamingPlatform(str, Enum):
    DOUYIN = "douyin"
    BILIBILI = "bilibili"
    YOUTUBE = "youtube"
    TWITCH = "twitch"


class Settings(BaseSettings):
    """Main configuration settings"""
    
    # Application settings
    app_name: str = "AI Voice Streaming Host"
    version: str = "1.0.0"
    debug: bool = False
    
    # Voice engine settings
    primary_voice_engine: VoiceEngine = VoiceEngine.XTTS_V2
    fallback_voice_engine: VoiceEngine = VoiceEngine.CHATTTS
    
    # Model paths
    models_dir: str = "models"
    voices_dir: str = "voices"
    cache_dir: str = "cache"
    
    # Audio settings
    sample_rate: int = 22050
    audio_format: str = "wav"
    chunk_size: int = 1024
    channels: int = 1
    
    # Streaming settings
    streaming_platform: StreamingPlatform = StreamingPlatform.DOUYIN
    stream_quality: str = "high"  # low, medium, high
    max_latency_ms: int = 200
    buffer_size: int = 4096
    
    # Language settings
    default_language: Language = Language.AUTO
    supported_languages: list = [Language.CHINESE, Language.ENGLISH]
    
    # Performance settings
    use_gpu: bool = True
    max_concurrent_requests: int = 5
    model_cache_size: int = 3
    
    # API settings
    api_host: str = "localhost"
    api_port: int = 8000
    websocket_port: int = 8001
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        env_prefix = "AIVOICE_"


class VoiceProfile:
    """Voice profile configuration"""
    
    def __init__(
        self,
        name: str,
        gender: str = "female",
        age_range: str = "young",
        language: str = "auto",
        pitch: float = 1.0,
        speed: float = 1.0,
        emotion: str = "neutral",
        voice_sample_path: Optional[str] = None
    ):
        self.name = name
        self.gender = gender
        self.age_range = age_range
        self.language = language
        self.pitch = pitch
        self.speed = speed
        self.emotion = emotion
        self.voice_sample_path = voice_sample_path
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "gender": self.gender,
            "age_range": self.age_range,
            "language": self.language,
            "pitch": self.pitch,
            "speed": self.speed,
            "emotion": self.emotion,
            "voice_sample_path": self.voice_sample_path
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def update_settings(**kwargs) -> None:
    """Update settings dynamically"""
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)


def create_directories() -> None:
    """Create necessary directories"""
    directories = [
        settings.models_dir,
        settings.voices_dir,
        settings.cache_dir,
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Initialize directories on import
create_directories()

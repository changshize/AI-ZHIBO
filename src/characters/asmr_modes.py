"""
ASMR Modes - Specialized configurations for ASMR content
"""
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from ..config import VoiceProfile

logger = logging.getLogger(__name__)


class ASMRTriggerType(str, Enum):
    WHISPERING = "whispering"
    TAPPING = "tapping"
    BRUSHING = "brushing"
    RAIN_SOUNDS = "rain_sounds"
    BREATHING = "breathing"
    MOUTH_SOUNDS = "mouth_sounds"
    ROLEPLAY = "roleplay"
    PERSONAL_ATTENTION = "personal_attention"


class ASMRMood(str, Enum):
    RELAXING = "relaxing"
    SLEEPY = "sleepy"
    CARING = "caring"
    INTIMATE = "intimate"
    PEACEFUL = "peaceful"
    COMFORTING = "comforting"


@dataclass
class ASMRConfiguration:
    """ASMR mode configuration"""
    name: str
    description: str
    trigger_types: List[ASMRTriggerType]
    mood: ASMRMood
    voice_pitch: float = 0.8
    voice_speed: float = 0.6
    whisper_intensity: float = 0.7
    breathing_sounds: bool = True
    background_sounds: Optional[str] = None
    script_templates: List[str] = None
    
    def __post_init__(self):
        if self.script_templates is None:
            self.script_templates = []


class ASMRManager:
    """Manages ASMR modes and triggers"""
    
    def __init__(self):
        self.asmr_modes: Dict[str, ASMRConfiguration] = {}
        self.current_mode: Optional[ASMRConfiguration] = None
        self.trigger_sounds: Dict[ASMRTriggerType, List[str]] = {}
        self._load_default_modes()
        self._load_trigger_sounds()
    
    def _load_default_modes(self):
        """Load default ASMR configurations"""
        
        # Gentle Whisper Mode
        self.asmr_modes["gentle_whisper"] = ASMRConfiguration(
            name="温柔耳语",
            description="轻柔的耳语声，让人放松入睡",
            trigger_types=[ASMRTriggerType.WHISPERING, ASMRTriggerType.BREATHING],
            mood=ASMRMood.SLEEPY,
            voice_pitch=0.7,
            voice_speed=0.5,
            whisper_intensity=0.8,
            breathing_sounds=True,
            script_templates=[
                "轻轻地... 闭上眼睛... 听我的声音...",
                "慢慢地... 深呼吸... 放松你的身体...",
                "Gently... close your eyes... listen to my voice...",
                "Slowly... breathe deeply... relax your body..."
            ]
        )
        
        # Personal Attention Mode
        self.asmr_modes["personal_attention"] = ASMRConfiguration(
            name="个人关怀",
            description="贴心的个人关怀，像姐姐一样照顾你",
            trigger_types=[ASMRTriggerType.PERSONAL_ATTENTION, ASMRTriggerType.WHISPERING],
            mood=ASMRMood.CARING,
            voice_pitch=0.9,
            voice_speed=0.7,
            whisper_intensity=0.6,
            breathing_sounds=False,
            script_templates=[
                "你今天辛苦了... 让我来照顾你...",
                "来... 躺下休息一会儿... 我在这里陪着你...",
                "You've worked hard today... let me take care of you...",
                "Come... lie down and rest... I'm here with you..."
            ]
        )
        
        # Rain & Nature Mode
        self.asmr_modes["rain_nature"] = ASMRConfiguration(
            name="雨声自然",
            description="配合雨声和自然音效的放松模式",
            trigger_types=[ASMRTriggerType.RAIN_SOUNDS, ASMRTriggerType.WHISPERING],
            mood=ASMRMood.PEACEFUL,
            voice_pitch=0.8,
            voice_speed=0.6,
            whisper_intensity=0.5,
            breathing_sounds=True,
            background_sounds="rain",
            script_templates=[
                "听... 外面下雨了... 很舒服对吧...",
                "雨滴轻轻敲打着窗户... 就像大自然的摇篮曲...",
                "Listen... it's raining outside... so peaceful...",
                "Raindrops gently tapping the window... like nature's lullaby..."
            ]
        )
        
        # Tapping & Sounds Mode
        self.asmr_modes["tapping_sounds"] = ASMRConfiguration(
            name="敲击音效",
            description="各种敲击和触摸音效，刺激听觉",
            trigger_types=[ASMRTriggerType.TAPPING, ASMRTriggerType.BRUSHING],
            mood=ASMRMood.RELAXING,
            voice_pitch=0.9,
            voice_speed=0.8,
            whisper_intensity=0.4,
            breathing_sounds=False,
            script_templates=[
                "听听这个声音... *轻敲* 很舒服吧...",
                "我用手指轻轻敲击... *tap tap* 放松一下...",
                "Listen to this sound... *gentle tapping* so soothing...",
                "I'm gently tapping with my fingers... *tap tap* just relax..."
            ]
        )
        
        # Roleplay Mode
        self.asmr_modes["roleplay"] = ASMRConfiguration(
            name="角色扮演",
            description="各种角色扮演场景，增加沉浸感",
            trigger_types=[ASMRTriggerType.ROLEPLAY, ASMRTriggerType.PERSONAL_ATTENTION],
            mood=ASMRMood.INTIMATE,
            voice_pitch=0.85,
            voice_speed=0.75,
            whisper_intensity=0.7,
            breathing_sounds=True,
            script_templates=[
                "欢迎来到我的小屋... 今天想要什么服务呢...",
                "让我来帮你按摩一下... 放松肩膀...",
                "Welcome to my little space... what would you like today...",
                "Let me give you a massage... relax your shoulders..."
            ]
        )
        
        logger.info(f"Loaded {len(self.asmr_modes)} ASMR modes")
    
    def _load_trigger_sounds(self):
        """Load trigger sound descriptions"""
        self.trigger_sounds = {
            ASMRTriggerType.WHISPERING: [
                "*轻声耳语*", "*温柔低语*", "*贴耳细语*",
                "*gentle whisper*", "*soft murmur*", "*quiet voice*"
            ],
            ASMRTriggerType.TAPPING: [
                "*轻敲桌面*", "*指尖敲击*", "*节奏敲打*",
                "*gentle tapping*", "*finger taps*", "*rhythmic tapping*"
            ],
            ASMRTriggerType.BRUSHING: [
                "*轻柔刷拭*", "*毛刷声音*", "*温柔抚摸*",
                "*gentle brushing*", "*soft brush sounds*", "*tender stroking*"
            ],
            ASMRTriggerType.RAIN_SOUNDS: [
                "*雨滴声*", "*细雨绵绵*", "*雨水敲窗*",
                "*rain drops*", "*gentle rain*", "*rain on window*"
            ],
            ASMRTriggerType.BREATHING: [
                "*轻柔呼吸*", "*深呼吸*", "*平静呼吸*",
                "*gentle breathing*", "*deep breath*", "*calm breathing*"
            ],
            ASMRTriggerType.MOUTH_SOUNDS: [
                "*轻吻声*", "*唇音*", "*口腔音*",
                "*kiss sounds*", "*lip sounds*", "*mouth sounds*"
            ]
        }
    
    def set_asmr_mode(self, mode_name: str) -> bool:
        """Set current ASMR mode"""
        try:
            if mode_name in self.asmr_modes:
                self.current_mode = self.asmr_modes[mode_name]
                logger.info(f"Switched to ASMR mode: {mode_name}")
                return True
            else:
                logger.error(f"ASMR mode not found: {mode_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to set ASMR mode: {e}")
            return False
    
    def get_asmr_voice_profile(self) -> VoiceProfile:
        """Get voice profile for current ASMR mode"""
        if not self.current_mode:
            # Default ASMR profile
            return VoiceProfile(
                name="default_asmr",
                gender="female",
                age_range="young",
                pitch=0.8,
                speed=0.6,
                emotion="calm"
            )
        
        return VoiceProfile(
            name=self.current_mode.name,
            gender="female",
            age_range="young",
            pitch=self.current_mode.voice_pitch,
            speed=self.current_mode.voice_speed,
            emotion=self.current_mode.mood.value
        )
    
    def generate_asmr_text(self, base_text: str = "", trigger_type: Optional[ASMRTriggerType] = None) -> str:
        """Generate ASMR-enhanced text with triggers"""
        try:
            if not self.current_mode:
                return base_text
            
            # Use provided trigger or random from current mode
            if trigger_type and trigger_type in self.current_mode.trigger_types:
                selected_trigger = trigger_type
            else:
                selected_trigger = random.choice(self.current_mode.trigger_types)
            
            # Get trigger sounds
            trigger_sounds = self.trigger_sounds.get(selected_trigger, [])
            
            # Generate text
            if base_text:
                # Enhance existing text
                enhanced_text = base_text
                
                # Add trigger sounds
                if trigger_sounds and random.random() < 0.7:
                    trigger_sound = random.choice(trigger_sounds)
                    enhanced_text = f"{enhanced_text} {trigger_sound}"
                
                # Add breathing pauses for whisper mode
                if selected_trigger == ASMRTriggerType.WHISPERING:
                    enhanced_text = enhanced_text.replace("。", "... ")
                    enhanced_text = enhanced_text.replace(".", "... ")
                
                return enhanced_text
            else:
                # Use template
                if self.current_mode.script_templates:
                    template = random.choice(self.current_mode.script_templates)
                    
                    # Add trigger sounds
                    if trigger_sounds and random.random() < 0.5:
                        trigger_sound = random.choice(trigger_sounds)
                        template = f"{template} {trigger_sound}"
                    
                    return template
                else:
                    return "轻轻地... 放松一下... Gently... just relax..."
                    
        except Exception as e:
            logger.error(f"Failed to generate ASMR text: {e}")
            return base_text or "放松... relax..."
    
    def get_background_sound(self) -> Optional[str]:
        """Get background sound for current mode"""
        if self.current_mode:
            return self.current_mode.background_sounds
        return None
    
    def add_custom_mode(self, mode: ASMRConfiguration) -> bool:
        """Add custom ASMR mode"""
        try:
            self.asmr_modes[mode.name] = mode
            logger.info(f"Added custom ASMR mode: {mode.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom ASMR mode: {e}")
            return False
    
    def get_available_modes(self) -> List[str]:
        """Get list of available ASMR modes"""
        return list(self.asmr_modes.keys())
    
    def get_current_mode(self) -> Optional[ASMRConfiguration]:
        """Get current ASMR mode"""
        return self.current_mode
    
    def get_trigger_types(self) -> List[ASMRTriggerType]:
        """Get available trigger types"""
        return list(ASMRTriggerType)
    
    def is_asmr_active(self) -> bool:
        """Check if ASMR mode is active"""
        return self.current_mode is not None

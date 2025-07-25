"""
Personality Manager - Handles different AI character personalities and behaviors
"""
import json
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from ..config import VoiceProfile

logger = logging.getLogger(__name__)


class PersonalityType(str, Enum):
    CUTE_GIRL = "cute_girl"
    ASMR_GIRL = "asmr_girl"
    ENERGETIC_GIRL = "energetic_girl"
    SHY_GIRL = "shy_girl"
    MATURE_SISTER = "mature_sister"
    PLAYFUL_GIRL = "playful_girl"
    SWEET_GIRL = "sweet_girl"
    COOL_GIRL = "cool_girl"


class EmotionState(str, Enum):
    HAPPY = "happy"
    EXCITED = "excited"
    CALM = "calm"
    SHY = "shy"
    PLAYFUL = "playful"
    SLEEPY = "sleepy"
    SURPRISED = "surprised"
    CARING = "caring"


@dataclass
class PersonalityTraits:
    """Personality traits configuration"""
    name: str
    description: str
    voice_pitch: float = 1.0
    voice_speed: float = 1.0
    emotion_tendency: EmotionState = EmotionState.HAPPY
    speaking_style: str = "normal"
    catchphrases: List[str] = None
    response_patterns: Dict[str, List[str]] = None
    voice_sample_path: Optional[str] = None
    
    def __post_init__(self):
        if self.catchphrases is None:
            self.catchphrases = []
        if self.response_patterns is None:
            self.response_patterns = {}


class PersonalityManager:
    """Manages different AI character personalities"""
    
    def __init__(self):
        self.personalities: Dict[str, PersonalityTraits] = {}
        self.current_personality: Optional[PersonalityTraits] = None
        self.emotion_modifiers: Dict[EmotionState, Dict[str, float]] = {}
        self._load_default_personalities()
        self._load_emotion_modifiers()
    
    def _load_default_personalities(self):
        """Load default personality configurations"""
        
        # Cute Girl - 可爱女孩
        self.personalities[PersonalityType.CUTE_GIRL] = PersonalityTraits(
            name="可爱小萌妹",
            description="甜美可爱的小女孩，声音清脆，喜欢用可爱的语气说话",
            voice_pitch=1.3,
            voice_speed=1.1,
            emotion_tendency=EmotionState.HAPPY,
            speaking_style="cute",
            catchphrases=[
                "哇~", "好棒哦~", "嘻嘻~", "么么哒~", "好开心呀~",
                "Wow~", "So cool~", "Hehe~", "Amazing~"
            ],
            response_patterns={
                "greeting": [
                    "大家好呀~ 我是你们的小萌妹~",
                    "嗨嗨~ 今天大家都好吗？",
                    "Hello everyone~ I'm your cute little host~"
                ],
                "thanks": [
                    "谢谢大家的支持~ 爱你们哦~",
                    "么么哒~ 你们真的太好了~",
                    "Thank you so much~ Love you all~"
                ],
                "excitement": [
                    "哇塞~ 太棒了！",
                    "好激动呀~ 心跳加速了~",
                    "OMG~ This is so exciting!"
                ]
            }
        )
        
        # ASMR Girl - ASMR女孩
        self.personalities[PersonalityType.ASMR_GIRL] = PersonalityTraits(
            name="温柔ASMR姐姐",
            description="声音轻柔温和，专门做ASMR内容，让人放松",
            voice_pitch=0.9,
            voice_speed=0.7,
            emotion_tendency=EmotionState.CALM,
            speaking_style="gentle",
            catchphrases=[
                "轻轻的~", "慢慢来~", "放松~", "很舒服~",
                "Gently~", "Slowly~", "Relax~", "So soothing~"
            ],
            response_patterns={
                "greeting": [
                    "大家好... 欢迎来到我的直播间... 让我们一起放松一下吧...",
                    "Hello everyone... Welcome to my stream... Let's relax together...",
                    "轻轻地说一声... 大家晚上好..."
                ],
                "asmr_triggers": [
                    "听听这个声音... 很舒服对吧...",
                    "慢慢地... 深呼吸... 放松你的身体...",
                    "Let the sound wash over you... so peaceful..."
                ],
                "goodnight": [
                    "晚安... 做个好梦...",
                    "Good night... Sweet dreams...",
                    "轻轻地... 闭上眼睛... 睡个好觉..."
                ]
            }
        )
        
        # Energetic Girl - 活力女孩
        self.personalities[PersonalityType.ENERGETIC_GIRL] = PersonalityTraits(
            name="活力满满小姐姐",
            description="充满活力和热情，说话快速有节奏",
            voice_pitch=1.4,
            voice_speed=1.3,
            emotion_tendency=EmotionState.EXCITED,
            speaking_style="energetic",
            catchphrases=[
                "冲冲冲！", "太棒了！", "加油！", "燃起来！", "超级棒！",
                "Let's go!", "Awesome!", "Amazing!", "So cool!", "Fantastic!"
            ],
            response_patterns={
                "greeting": [
                    "大家好！我是你们的活力小姐姐！今天要一起嗨起来！",
                    "Hello everyone! Ready to have some fun today?!",
                    "嗨！准备好跟我一起燃烧吗？！"
                ],
                "encouragement": [
                    "加油加油！你们都是最棒的！",
                    "Come on! You can do it! So amazing!",
                    "冲冲冲！一起燃起来！"
                ],
                "celebration": [
                    "耶！太棒了！我们做到了！",
                    "Yes! That was incredible! We did it!",
                    "哇！超级无敌棒！"
                ]
            }
        )
        
        # Shy Girl - 害羞女孩
        self.personalities[PersonalityType.SHY_GIRL] = PersonalityTraits(
            name="害羞小妹妹",
            description="性格害羞内向，说话轻声细语，容易脸红",
            voice_pitch=1.1,
            voice_speed=0.9,
            emotion_tendency=EmotionState.SHY,
            speaking_style="shy",
            catchphrases=[
                "那个...", "嗯...", "有点害羞...", "不好意思...",
                "Um...", "Well...", "I'm a bit shy...", "Sorry..."
            ],
            response_patterns={
                "greeting": [
                    "那个... 大家好... 我有点紧张...",
                    "Um... Hello everyone... I'm a bit nervous...",
                    "嗯... 请多多关照..."
                ],
                "compliment_received": [
                    "诶？真的吗... 谢谢... 好害羞...",
                    "Really? Thank you... I'm blushing...",
                    "不敢当... 大家太夸奖了..."
                ],
                "mistake": [
                    "啊... 对不起... 我搞错了...",
                    "Oh no... Sorry... I made a mistake...",
                    "嗯... 不好意思... 让我重新来..."
                ]
            }
        )
        
        logger.info(f"Loaded {len(self.personalities)} default personalities")
    
    def _load_emotion_modifiers(self):
        """Load emotion-based voice modifiers"""
        self.emotion_modifiers = {
            EmotionState.HAPPY: {"pitch": 1.1, "speed": 1.05},
            EmotionState.EXCITED: {"pitch": 1.3, "speed": 1.2},
            EmotionState.CALM: {"pitch": 0.9, "speed": 0.8},
            EmotionState.SHY: {"pitch": 1.0, "speed": 0.9},
            EmotionState.PLAYFUL: {"pitch": 1.2, "speed": 1.1},
            EmotionState.SLEEPY: {"pitch": 0.8, "speed": 0.7},
            EmotionState.SURPRISED: {"pitch": 1.4, "speed": 1.3},
            EmotionState.CARING: {"pitch": 0.95, "speed": 0.85}
        }
    
    def set_personality(self, personality_type: PersonalityType) -> bool:
        """Set current personality"""
        try:
            if personality_type in self.personalities:
                self.current_personality = self.personalities[personality_type]
                logger.info(f"Switched to personality: {personality_type}")
                return True
            else:
                logger.error(f"Personality not found: {personality_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to set personality: {e}")
            return False
    
    def get_voice_profile(self, emotion: Optional[EmotionState] = None) -> VoiceProfile:
        """Get voice profile based on current personality and emotion"""
        if not self.current_personality:
            # Return default profile
            return VoiceProfile(
                name="default",
                gender="female",
                age_range="young",
                pitch=1.0,
                speed=1.0
            )
        
        # Base voice settings from personality
        pitch = self.current_personality.voice_pitch
        speed = self.current_personality.voice_speed
        
        # Apply emotion modifiers
        if emotion and emotion in self.emotion_modifiers:
            modifiers = self.emotion_modifiers[emotion]
            pitch *= modifiers.get("pitch", 1.0)
            speed *= modifiers.get("speed", 1.0)
        elif self.current_personality.emotion_tendency in self.emotion_modifiers:
            modifiers = self.emotion_modifiers[self.current_personality.emotion_tendency]
            pitch *= modifiers.get("pitch", 1.0)
            speed *= modifiers.get("speed", 1.0)
        
        return VoiceProfile(
            name=self.current_personality.name,
            gender="female",
            age_range="young",
            pitch=pitch,
            speed=speed,
            emotion=emotion.value if emotion else self.current_personality.emotion_tendency.value,
            voice_sample_path=self.current_personality.voice_sample_path
        )
    
    def get_response_text(self, context: str, user_input: str = "") -> str:
        """Generate contextual response text based on personality"""
        if not self.current_personality:
            return user_input
        
        try:
            # Get response patterns for context
            patterns = self.current_personality.response_patterns.get(context, [])
            
            if patterns:
                # Choose random response pattern
                response = random.choice(patterns)
                
                # Add catchphrases occasionally
                if random.random() < 0.3 and self.current_personality.catchphrases:
                    catchphrase = random.choice(self.current_personality.catchphrases)
                    response = f"{response} {catchphrase}"
                
                return response
            else:
                # Fallback: add catchphrase to user input
                if self.current_personality.catchphrases and random.random() < 0.2:
                    catchphrase = random.choice(self.current_personality.catchphrases)
                    return f"{user_input} {catchphrase}"
                
                return user_input
                
        except Exception as e:
            logger.error(f"Failed to generate response text: {e}")
            return user_input
    
    def add_custom_personality(self, personality: PersonalityTraits) -> bool:
        """Add custom personality"""
        try:
            self.personalities[personality.name] = personality
            logger.info(f"Added custom personality: {personality.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom personality: {e}")
            return False
    
    def get_available_personalities(self) -> List[str]:
        """Get list of available personalities"""
        return list(self.personalities.keys())
    
    def get_current_personality(self) -> Optional[PersonalityTraits]:
        """Get current personality"""
        return self.current_personality
    
    def save_personalities(self, file_path: str) -> bool:
        """Save personalities to file"""
        try:
            data = {}
            for name, personality in self.personalities.items():
                data[name] = asdict(personality)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Personalities saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save personalities: {e}")
            return False
    
    def load_personalities(self, file_path: str) -> bool:
        """Load personalities from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for name, personality_data in data.items():
                personality = PersonalityTraits(**personality_data)
                self.personalities[name] = personality
            
            logger.info(f"Personalities loaded from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load personalities: {e}")
            return False

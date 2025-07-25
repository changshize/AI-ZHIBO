"""
Emotion Detector - Detects emotions from text for voice modulation
"""
import re
import logging
from typing import List, Dict, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class EmotionType(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    ANGRY = "angry"
    SURPRISED = "surprised"
    CALM = "calm"
    LOVE = "love"
    FEAR = "fear"
    SLEEPY = "sleepy"
    PLAYFUL = "playful"


class EmotionDetector:
    """Detects emotions from text content"""
    
    def __init__(self):
        self.emotion_keywords = self._load_emotion_keywords()
        self.emotion_patterns = self._load_emotion_patterns()
        self.punctuation_emotions = self._load_punctuation_emotions()
    
    def _load_emotion_keywords(self) -> Dict[EmotionType, List[str]]:
        """Load emotion keywords for different languages"""
        return {
            EmotionType.HAPPY: [
                # Chinese
                "开心", "高兴", "快乐", "愉快", "兴奋", "喜悦", "欢乐", "幸福",
                "哈哈", "嘻嘻", "呵呵", "嘿嘿", "笑", "乐",
                # English
                "happy", "joy", "glad", "cheerful", "delighted", "pleased",
                "excited", "thrilled", "wonderful", "amazing", "awesome",
                "haha", "hehe", "lol", "laugh", "smile"
            ],
            EmotionType.SAD: [
                # Chinese
                "伤心", "难过", "悲伤", "痛苦", "沮丧", "失望", "郁闷", "忧伤",
                "哭", "泪", "眼泪", "呜呜", "555",
                # English
                "sad", "sorrow", "grief", "upset", "depressed", "disappointed",
                "hurt", "pain", "cry", "tears", "sob"
            ],
            EmotionType.EXCITED: [
                # Chinese
                "激动", "兴奋", "热血", "燃", "冲", "爽", "棒", "赞",
                "哇", "哇塞", "太棒了", "厉害", "牛", "6666",
                # English
                "excited", "thrilled", "pumped", "energetic", "amazing",
                "wow", "awesome", "incredible", "fantastic", "cool"
            ],
            EmotionType.ANGRY: [
                # Chinese
                "生气", "愤怒", "气愤", "恼火", "火大", "烦", "讨厌", "恨",
                "靠", "草", "妈的", "该死", "混蛋",
                # English
                "angry", "mad", "furious", "annoyed", "irritated", "pissed",
                "hate", "damn", "hell", "stupid", "idiot"
            ],
            EmotionType.SURPRISED: [
                # Chinese
                "惊讶", "震惊", "吃惊", "意外", "没想到", "天哪", "我的天",
                "哇", "咦", "诶", "啊", "哎呀",
                # English
                "surprised", "shocked", "amazed", "astonished", "wow",
                "omg", "oh my god", "what", "really", "no way"
            ],
            EmotionType.CALM: [
                # Chinese
                "平静", "冷静", "安静", "宁静", "放松", "舒服", "淡定",
                "嗯", "好的", "知道了", "明白",
                # English
                "calm", "peaceful", "quiet", "relaxed", "serene", "tranquil",
                "okay", "alright", "fine", "cool"
            ],
            EmotionType.LOVE: [
                # Chinese
                "爱", "喜欢", "爱你", "亲爱的", "宝贝", "心", "❤️",
                "么么哒", "亲亲", "抱抱", "爱心", "甜蜜",
                # English
                "love", "like", "adore", "dear", "honey", "baby", "heart",
                "kiss", "hug", "sweet", "cute", "adorable"
            ],
            EmotionType.SLEEPY: [
                # Chinese
                "困", "累", "疲惫", "想睡", "睡觉", "休息", "打哈欠",
                "呼呼", "zzz", "💤", "😴",
                # English
                "tired", "sleepy", "exhausted", "yawn", "sleep", "rest",
                "zzz", "drowsy", "weary"
            ],
            EmotionType.PLAYFUL: [
                # Chinese
                "玩", "游戏", "有趣", "好玩", "调皮", "淘气", "搞怪",
                "嘿嘿", "嘻嘻", "哈哈", "逗", "萌",
                # English
                "play", "fun", "funny", "playful", "silly", "cute",
                "game", "joke", "tease", "mischief"
            ]
        }
    
    def _load_emotion_patterns(self) -> Dict[EmotionType, List[str]]:
        """Load regex patterns for emotion detection"""
        return {
            EmotionType.HAPPY: [
                r"[哈嘻呵嘿]{2,}",  # 哈哈, 嘻嘻, etc.
                r"[6]{3,}",         # 666...
                r"[!]{2,}",         # !!!
                r"太.*了",          # 太好了, 太棒了
            ],
            EmotionType.SAD: [
                r"[呜]{2,}",        # 呜呜
                r"[5]{3,}",         # 555
                r"T[_T]{1,}T",      # T_T
                r"[泪眼].*[流下]",   # 泪流, 眼泪下
            ],
            EmotionType.EXCITED: [
                r"[哇]{2,}",        # 哇哇
                r"[冲]{1,}[啊鸭]",   # 冲啊
                r"[燃爽]{1,}",      # 燃, 爽
            ],
            EmotionType.SURPRISED: [
                r"[咦诶]{1,}",      # 咦, 诶
                r"什么[？?!]{1,}",   # 什么？
                r"天[哪啊][！!]{0,}", # 天哪！
            ]
        }
    
    def _load_punctuation_emotions(self) -> Dict[str, EmotionType]:
        """Load punctuation-based emotion indicators"""
        return {
            "!!!": EmotionType.EXCITED,
            "???": EmotionType.SURPRISED,
            "...": EmotionType.CALM,
            "~~~": EmotionType.PLAYFUL,
            "💔": EmotionType.SAD,
            "❤️": EmotionType.LOVE,
            "😴": EmotionType.SLEEPY,
            "🔥": EmotionType.EXCITED,
        }
    
    def detect_emotions(self, text: str) -> List[Tuple[EmotionType, float]]:
        """
        Detect emotions in text
        
        Returns:
            List of (emotion, confidence) tuples
        """
        emotions = {}
        text_lower = text.lower()
        
        # Keyword-based detection
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            
            if score > 0:
                # Normalize score
                confidence = min(score / len(keywords) * 10, 1.0)
                emotions[emotion] = max(emotions.get(emotion, 0), confidence)
        
        # Pattern-based detection
        for emotion, patterns in self.emotion_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    confidence = min(len(matches) * 0.3, 1.0)
                    emotions[emotion] = max(emotions.get(emotion, 0), confidence)
        
        # Punctuation-based detection
        for punct, emotion in self.punctuation_emotions.items():
            if punct in text:
                confidence = 0.5
                emotions[emotion] = max(emotions.get(emotion, 0), confidence)
        
        # Sort by confidence
        result = [(emotion, confidence) for emotion, confidence in emotions.items()]
        result.sort(key=lambda x: x[1], reverse=True)
        
        return result
    
    def get_primary_emotion(self, text: str) -> Optional[EmotionType]:
        """Get the primary emotion from text"""
        emotions = self.detect_emotions(text)
        return emotions[0][0] if emotions else None
    
    def get_emotion_intensity(self, text: str, emotion: EmotionType) -> float:
        """Get intensity of specific emotion in text"""
        emotions = self.detect_emotions(text)
        for detected_emotion, confidence in emotions:
            if detected_emotion == emotion:
                return confidence
        return 0.0
    
    def analyze_emotional_context(self, text: str) -> Dict[str, any]:
        """Comprehensive emotional analysis"""
        emotions = self.detect_emotions(text)
        
        analysis = {
            "primary_emotion": emotions[0][0] if emotions else None,
            "primary_confidence": emotions[0][1] if emotions else 0.0,
            "all_emotions": emotions,
            "emotional_intensity": sum(conf for _, conf in emotions),
            "is_emotional": len(emotions) > 0,
            "emotion_count": len(emotions)
        }
        
        # Determine overall emotional state
        if analysis["emotional_intensity"] > 0.7:
            analysis["emotional_state"] = "highly_emotional"
        elif analysis["emotional_intensity"] > 0.3:
            analysis["emotional_state"] = "moderately_emotional"
        else:
            analysis["emotional_state"] = "neutral"
        
        return analysis
    
    def suggest_voice_adjustments(self, text: str) -> Dict[str, float]:
        """Suggest voice parameter adjustments based on emotions"""
        primary_emotion = self.get_primary_emotion(text)
        
        if not primary_emotion:
            return {"pitch": 1.0, "speed": 1.0, "volume": 1.0}
        
        # Emotion-based voice adjustments
        adjustments = {
            EmotionType.HAPPY: {"pitch": 1.2, "speed": 1.1, "volume": 1.1},
            EmotionType.SAD: {"pitch": 0.8, "speed": 0.8, "volume": 0.9},
            EmotionType.EXCITED: {"pitch": 1.3, "speed": 1.3, "volume": 1.2},
            EmotionType.ANGRY: {"pitch": 1.1, "speed": 1.2, "volume": 1.3},
            EmotionType.SURPRISED: {"pitch": 1.4, "speed": 1.2, "volume": 1.1},
            EmotionType.CALM: {"pitch": 0.9, "speed": 0.8, "volume": 0.9},
            EmotionType.LOVE: {"pitch": 1.1, "speed": 0.9, "volume": 1.0},
            EmotionType.SLEEPY: {"pitch": 0.7, "speed": 0.6, "volume": 0.8},
            EmotionType.PLAYFUL: {"pitch": 1.2, "speed": 1.1, "volume": 1.0}
        }
        
        return adjustments.get(primary_emotion, {"pitch": 1.0, "speed": 1.0, "volume": 1.0})
    
    def add_emotional_markers(self, text: str, emotion: EmotionType) -> str:
        """Add emotional markers to text for TTS"""
        markers = {
            EmotionType.HAPPY: " *cheerful* ",
            EmotionType.SAD: " *sad* ",
            EmotionType.EXCITED: " *excited* ",
            EmotionType.ANGRY: " *angry* ",
            EmotionType.SURPRISED: " *surprised* ",
            EmotionType.CALM: " *calm* ",
            EmotionType.LOVE: " *loving* ",
            EmotionType.SLEEPY: " *sleepy* ",
            EmotionType.PLAYFUL: " *playful* "
        }
        
        marker = markers.get(emotion, "")
        return f"{marker}{text}{marker}"

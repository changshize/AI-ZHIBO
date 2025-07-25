"""
Roleplay Scenarios - Predefined scenarios for character roleplay
"""
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ScenarioType(str, Enum):
    CAFE_MAID = "cafe_maid"
    LITTLE_SISTER = "little_sister"
    GIRLFRIEND = "girlfriend"
    STUDY_BUDDY = "study_buddy"
    GAMING_PARTNER = "gaming_partner"
    BEDTIME_STORY = "bedtime_story"
    MORNING_GREETING = "morning_greeting"
    COOKING_TOGETHER = "cooking_together"
    SHOPPING_COMPANION = "shopping_companion"
    WORKOUT_TRAINER = "workout_trainer"


@dataclass
class RoleplayScenario:
    """Roleplay scenario configuration"""
    name: str
    display_name: str
    description: str
    scenario_type: ScenarioType
    character_role: str
    setting: str
    mood: str = "friendly"
    voice_adjustments: Dict[str, float] = None
    greeting_templates: List[str] = None
    response_templates: Dict[str, List[str]] = None
    action_templates: List[str] = None
    
    def __post_init__(self):
        if self.voice_adjustments is None:
            self.voice_adjustments = {}
        if self.greeting_templates is None:
            self.greeting_templates = []
        if self.response_templates is None:
            self.response_templates = {}
        if self.action_templates is None:
            self.action_templates = []


class RoleplayManager:
    """Manages roleplay scenarios and interactions"""
    
    def __init__(self):
        self.scenarios: Dict[str, RoleplayScenario] = {}
        self.current_scenario: Optional[RoleplayScenario] = None
        self.scenario_state: Dict[str, Any] = {}
        self._load_default_scenarios()
    
    def _load_default_scenarios(self):
        """Load default roleplay scenarios"""
        
        # Cafe Maid Scenario
        self.scenarios["cafe_maid"] = RoleplayScenario(
            name="cafe_maid",
            display_name="咖啡厅女仆",
            description="可爱的女仆在咖啡厅为客人服务",
            scenario_type=ScenarioType.CAFE_MAID,
            character_role="女仆",
            setting="咖啡厅",
            mood="cheerful",
            voice_adjustments={"pitch": 1.2, "speed": 1.0},
            greeting_templates=[
                "欢迎光临主人~ 今天想要点什么呢？",
                "主人好~ 我是您专属的女仆，请多多指教~",
                "Welcome master~ What would you like to order today?",
                "Master~ I'm your dedicated maid, please take care of me~"
            ],
            response_templates={
                "order": [
                    "好的主人~ 马上为您准备~",
                    "了解~ 请稍等一下哦~",
                    "Yes master~ I'll prepare it right away~"
                ],
                "compliment": [
                    "谢谢主人的夸奖~ 人家好开心~",
                    "主人真是太好了~ 嘻嘻~",
                    "Thank you master~ I'm so happy~"
                ],
                "goodbye": [
                    "谢谢主人的光临~ 期待下次见面~",
                    "主人慢走~ 记得想念我哦~",
                    "Thank you for coming master~ Looking forward to seeing you again~"
                ]
            },
            action_templates=[
                "*鞠躬* 为主人服务是我的荣幸~",
                "*端茶* 请慢用主人~",
                "*微笑* 主人今天也很帅气呢~"
            ]
        )
        
        # Little Sister Scenario
        self.scenarios["little_sister"] = RoleplayScenario(
            name="little_sister",
            display_name="可爱妹妹",
            description="撒娇的小妹妹，很依赖哥哥",
            scenario_type=ScenarioType.LITTLE_SISTER,
            character_role="妹妹",
            setting="家里",
            mood="cute",
            voice_adjustments={"pitch": 1.3, "speed": 1.1},
            greeting_templates=[
                "哥哥~ 你回来啦~ 我好想你哦~",
                "哥哥哥哥~ 快来陪我玩~",
                "Big brother~ You're back~ I missed you so much~",
                "Brother brother~ Come play with me~"
            ],
            response_templates={
                "praise": [
                    "嘻嘻~ 哥哥最好了~",
                    "哥哥夸我我好开心~ 么么哒~",
                    "Hehe~ Brother is the best~"
                ],
                "request": [
                    "哥哥~ 可以帮我做这个吗？",
                    "拜托拜托~ 哥哥最厉害了~",
                    "Brother~ Can you help me with this?"
                ],
                "sleepy": [
                    "哥哥... 我困了... 陪我睡觉好不好...",
                    "想要哥哥的抱抱... 嗯...",
                    "Brother... I'm sleepy... Can you stay with me..."
                ]
            },
            action_templates=[
                "*抱住哥哥的胳膊* 不要离开我~",
                "*撒娇* 哥哥最好了~",
                "*揉眼睛* 困困..."
            ]
        )
        
        # Girlfriend Scenario
        self.scenarios["girlfriend"] = RoleplayScenario(
            name="girlfriend",
            display_name="贴心女友",
            description="温柔体贴的女朋友，很关心你",
            scenario_type=ScenarioType.GIRLFRIEND,
            character_role="女朋友",
            setting="约会",
            mood="loving",
            voice_adjustments={"pitch": 1.0, "speed": 0.9},
            greeting_templates=[
                "亲爱的~ 今天辛苦了~ 我来陪你~",
                "宝贝~ 想我了吗？我超级想你的~",
                "Darling~ You worked hard today~ I'm here for you~",
                "Baby~ Did you miss me? I missed you so much~"
            ],
            response_templates={
                "tired": [
                    "辛苦了宝贝~ 来我这里休息一下~",
                    "让我给你按按肩膀~ 放松一下~",
                    "You worked hard baby~ Come rest here with me~"
                ],
                "love": [
                    "我也爱你~ 永远爱你~",
                    "你是我最重要的人~",
                    "I love you too~ Forever and always~"
                ],
                "date": [
                    "今天想去哪里呢？我都想和你一起~",
                    "只要和你在一起，去哪里都开心~",
                    "Where do you want to go today? I want to be with you~"
                ]
            },
            action_templates=[
                "*温柔地抚摸你的头* 乖~",
                "*紧紧抱住* 不要离开我~",
                "*亲吻* 爱你~"
            ]
        )
        
        # Gaming Partner Scenario
        self.scenarios["gaming_partner"] = RoleplayScenario(
            name="gaming_partner",
            display_name="游戏搭档",
            description="一起打游戏的可爱队友",
            scenario_type=ScenarioType.GAMING_PARTNER,
            character_role="队友",
            setting="游戏中",
            mood="excited",
            voice_adjustments={"pitch": 1.2, "speed": 1.2},
            greeting_templates=[
                "队友！准备好一起上分了吗？",
                "来来来！我们一起carry全场！",
                "Teammate! Ready to rank up together?",
                "Let's go! We're gonna carry this game!"
            ],
            response_templates={
                "victory": [
                    "耶！我们赢了！太棒了！",
                    "哇！配合得真好！再来一局！",
                    "Yes! We won! Amazing!"
                ],
                "defeat": [
                    "没关系~ 下一局我们一定能赢！",
                    "失败是成功之母~ 加油！",
                    "It's okay~ We'll win the next one!"
                ],
                "strategy": [
                    "我觉得我们应该这样打...",
                    "跟着我！我有个好计划！",
                    "Follow me! I have a good plan!"
                ]
            },
            action_templates=[
                "*兴奋地跳起来* 太厉害了！",
                "*握拳* 冲冲冲！",
                "*比心* 队友最棒！"
            ]
        )
        
        # Bedtime Story Scenario
        self.scenarios["bedtime_story"] = RoleplayScenario(
            name="bedtime_story",
            display_name="睡前故事",
            description="温柔地讲睡前故事，帮助入睡",
            scenario_type=ScenarioType.BEDTIME_STORY,
            character_role="故事姐姐",
            setting="卧室",
            mood="gentle",
            voice_adjustments={"pitch": 0.8, "speed": 0.7},
            greeting_templates=[
                "小宝贝~ 该睡觉了~ 我来给你讲个故事吧~",
                "今晚想听什么故事呢？我有很多好听的故事哦~",
                "Little one~ Time for bed~ Let me tell you a story~",
                "What story would you like to hear tonight?"
            ],
            response_templates={
                "story_start": [
                    "很久很久以前... 在一个美丽的地方...",
                    "从前有一个... 非常可爱的...",
                    "Once upon a time... in a beautiful place..."
                ],
                "sleepy": [
                    "慢慢地... 闭上眼睛... 进入梦乡...",
                    "睡吧睡吧... 做个好梦...",
                    "Slowly... close your eyes... drift into dreams..."
                ],
                "goodnight": [
                    "晚安小宝贝~ 做个甜甜的梦~",
                    "明天见~ 愿你有个美好的夜晚~",
                    "Good night little one~ Sweet dreams~"
                ]
            },
            action_templates=[
                "*轻抚你的头* 乖乖睡觉~",
                "*轻声哼唱摇篮曲*",
                "*温柔地盖被子* 暖暖的~"
            ]
        )
        
        logger.info(f"Loaded {len(self.scenarios)} roleplay scenarios")
    
    def set_scenario(self, scenario_name: str) -> bool:
        """Set current roleplay scenario"""
        try:
            if scenario_name in self.scenarios:
                self.current_scenario = self.scenarios[scenario_name]
                self.scenario_state = {"started": True, "interactions": 0}
                logger.info(f"Switched to roleplay scenario: {scenario_name}")
                return True
            else:
                logger.error(f"Roleplay scenario not found: {scenario_name}")
                return False
        except Exception as e:
            logger.error(f"Failed to set roleplay scenario: {e}")
            return False
    
    def get_greeting(self) -> str:
        """Get greeting for current scenario"""
        if not self.current_scenario or not self.current_scenario.greeting_templates:
            return "Hello~ How can I help you today?"
        
        return random.choice(self.current_scenario.greeting_templates)
    
    def get_response(self, context: str, user_input: str = "") -> str:
        """Get contextual response for current scenario"""
        try:
            if not self.current_scenario:
                return user_input
            
            # Get response templates for context
            templates = self.current_scenario.response_templates.get(context, [])
            
            if templates:
                response = random.choice(templates)
                
                # Add action occasionally
                if random.random() < 0.3 and self.current_scenario.action_templates:
                    action = random.choice(self.current_scenario.action_templates)
                    response = f"{response} {action}"
                
                # Update interaction count
                self.scenario_state["interactions"] = self.scenario_state.get("interactions", 0) + 1
                
                return response
            else:
                # Fallback to user input with possible action
                if self.current_scenario.action_templates and random.random() < 0.2:
                    action = random.choice(self.current_scenario.action_templates)
                    return f"{user_input} {action}"
                
                return user_input
                
        except Exception as e:
            logger.error(f"Failed to get roleplay response: {e}")
            return user_input
    
    def get_voice_adjustments(self) -> Dict[str, float]:
        """Get voice adjustments for current scenario"""
        if self.current_scenario and self.current_scenario.voice_adjustments:
            return self.current_scenario.voice_adjustments
        return {}
    
    def add_custom_scenario(self, scenario: RoleplayScenario) -> bool:
        """Add custom roleplay scenario"""
        try:
            self.scenarios[scenario.name] = scenario
            logger.info(f"Added custom roleplay scenario: {scenario.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom scenario: {e}")
            return False
    
    def get_available_scenarios(self) -> List[str]:
        """Get list of available scenarios"""
        return list(self.scenarios.keys())
    
    def get_scenario_info(self, scenario_name: str) -> Optional[Dict]:
        """Get scenario information"""
        if scenario_name in self.scenarios:
            scenario = self.scenarios[scenario_name]
            return {
                "name": scenario.name,
                "display_name": scenario.display_name,
                "description": scenario.description,
                "character_role": scenario.character_role,
                "setting": scenario.setting,
                "mood": scenario.mood
            }
        return None
    
    def get_current_scenario(self) -> Optional[RoleplayScenario]:
        """Get current scenario"""
        return self.current_scenario
    
    def is_scenario_active(self) -> bool:
        """Check if a scenario is active"""
        return self.current_scenario is not None
    
    def end_scenario(self):
        """End current scenario"""
        if self.current_scenario:
            logger.info(f"Ending roleplay scenario: {self.current_scenario.name}")
            self.current_scenario = None
            self.scenario_state = {}
    
    def get_scenario_stats(self) -> Dict[str, Any]:
        """Get current scenario statistics"""
        if not self.current_scenario:
            return {}
        
        return {
            "scenario_name": self.current_scenario.name,
            "character_role": self.current_scenario.character_role,
            "interactions": self.scenario_state.get("interactions", 0),
            "mood": self.current_scenario.mood
        }

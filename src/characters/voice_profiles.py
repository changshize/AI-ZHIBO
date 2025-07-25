"""
Voice Profiles Manager - Manages voice configurations and samples
"""
import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

from ..config import VoiceProfile, settings

logger = logging.getLogger(__name__)


@dataclass
class VoiceCharacter:
    """Extended voice character with samples and metadata"""
    name: str
    display_name: str
    description: str
    gender: str = "female"
    age_range: str = "young"
    language: str = "auto"
    voice_sample_path: Optional[str] = None
    reference_samples: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.reference_samples is None:
            self.reference_samples = []
        if self.tags is None:
            self.tags = []


class VoiceProfileManager:
    """Manages voice profiles and character voices"""
    
    def __init__(self):
        self.voice_characters: Dict[str, VoiceCharacter] = {}
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.sample_directory = settings.voices_dir
        self._load_default_characters()
    
    def _load_default_characters(self):
        """Load default voice characters"""
        
        # Cute Girl Characters
        self.voice_characters["moe_chan"] = VoiceCharacter(
            name="moe_chan",
            display_name="萌萌酱",
            description="超级可爱的萌妹子，声音甜美清脆",
            gender="female",
            age_range="young",
            language="zh",
            tags=["cute", "sweet", "young", "chinese"]
        )
        
        self.voice_characters["kawaii_girl"] = VoiceCharacter(
            name="kawaii_girl", 
            display_name="Kawaii Girl",
            description="Adorable anime-style voice, perfect for cute content",
            gender="female",
            age_range="young",
            language="en",
            tags=["kawaii", "anime", "cute", "english"]
        )
        
        # ASMR Characters
        self.voice_characters["asmr_nee_san"] = VoiceCharacter(
            name="asmr_nee_san",
            display_name="ASMR姐姐",
            description="温柔的ASMR声音，专门用于放松内容",
            gender="female",
            age_range="mature",
            language="zh",
            tags=["asmr", "gentle", "relaxing", "chinese"]
        )
        
        self.voice_characters["whisper_angel"] = VoiceCharacter(
            name="whisper_angel",
            display_name="Whisper Angel",
            description="Soft, angelic whisper voice for ASMR content",
            gender="female",
            age_range="young",
            language="en",
            tags=["asmr", "whisper", "angelic", "english"]
        )
        
        # Energetic Characters
        self.voice_characters["genki_girl"] = VoiceCharacter(
            name="genki_girl",
            display_name="元气少女",
            description="充满活力的少女声音，适合高能内容",
            gender="female",
            age_range="young",
            language="zh",
            tags=["energetic", "cheerful", "young", "chinese"]
        )
        
        # Shy Characters
        self.voice_characters["shy_imouto"] = VoiceCharacter(
            name="shy_imouto",
            display_name="害羞妹妹",
            description="害羞内向的妹妹声音，很有治愈感",
            gender="female",
            age_range="young",
            language="zh",
            tags=["shy", "healing", "young", "chinese"]
        )
        
        logger.info(f"Loaded {len(self.voice_characters)} default voice characters")
    
    def create_voice_profile(self, character_name: str, **kwargs) -> Optional[VoiceProfile]:
        """Create voice profile from character"""
        try:
            if character_name not in self.voice_characters:
                logger.error(f"Voice character not found: {character_name}")
                return None
            
            character = self.voice_characters[character_name]
            
            # Default voice parameters based on character
            voice_params = {
                "name": character.name,
                "gender": character.gender,
                "age_range": character.age_range,
                "language": character.language,
                "voice_sample_path": character.voice_sample_path,
                "pitch": 1.0,
                "speed": 1.0,
                "emotion": "neutral"
            }
            
            # Apply character-specific defaults
            if "cute" in character.tags:
                voice_params.update({"pitch": 1.2, "emotion": "happy"})
            elif "asmr" in character.tags:
                voice_params.update({"pitch": 0.8, "speed": 0.7, "emotion": "calm"})
            elif "energetic" in character.tags:
                voice_params.update({"pitch": 1.3, "speed": 1.2, "emotion": "excited"})
            elif "shy" in character.tags:
                voice_params.update({"pitch": 1.0, "speed": 0.9, "emotion": "shy"})
            
            # Override with provided parameters
            voice_params.update(kwargs)
            
            profile = VoiceProfile(**voice_params)
            self.voice_profiles[character_name] = profile
            
            logger.info(f"Created voice profile for character: {character_name}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create voice profile: {e}")
            return None
    
    def get_voice_profile(self, character_name: str) -> Optional[VoiceProfile]:
        """Get voice profile for character"""
        if character_name in self.voice_profiles:
            return self.voice_profiles[character_name]
        else:
            # Create on-demand
            return self.create_voice_profile(character_name)
    
    def add_voice_sample(self, character_name: str, sample_path: str) -> bool:
        """Add voice sample to character"""
        try:
            if character_name not in self.voice_characters:
                logger.error(f"Voice character not found: {character_name}")
                return False
            
            if not os.path.exists(sample_path):
                logger.error(f"Voice sample file not found: {sample_path}")
                return False
            
            character = self.voice_characters[character_name]
            
            # Set as main sample if none exists
            if not character.voice_sample_path:
                character.voice_sample_path = sample_path
            
            # Add to reference samples
            if sample_path not in character.reference_samples:
                character.reference_samples.append(sample_path)
            
            # Update voice profile if exists
            if character_name in self.voice_profiles:
                self.voice_profiles[character_name].voice_sample_path = character.voice_sample_path
            
            logger.info(f"Added voice sample for {character_name}: {sample_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add voice sample: {e}")
            return False
    
    def clone_voice_from_sample(self, character_name: str, sample_path: str, new_character_name: str) -> bool:
        """Clone voice character from audio sample"""
        try:
            if not os.path.exists(sample_path):
                logger.error(f"Sample file not found: {sample_path}")
                return False
            
            # Create new character based on sample
            base_character = self.voice_characters.get(character_name)
            if base_character:
                # Clone from existing character
                new_character = VoiceCharacter(
                    name=new_character_name,
                    display_name=f"Cloned {base_character.display_name}",
                    description=f"Voice cloned from {base_character.name}",
                    gender=base_character.gender,
                    age_range=base_character.age_range,
                    language=base_character.language,
                    voice_sample_path=sample_path,
                    reference_samples=[sample_path],
                    tags=base_character.tags + ["cloned"]
                )
            else:
                # Create new character from scratch
                new_character = VoiceCharacter(
                    name=new_character_name,
                    display_name=f"Custom {new_character_name}",
                    description="Custom cloned voice",
                    voice_sample_path=sample_path,
                    reference_samples=[sample_path],
                    tags=["cloned", "custom"]
                )
            
            self.voice_characters[new_character_name] = new_character
            
            # Create voice profile
            self.create_voice_profile(new_character_name)
            
            logger.info(f"Cloned voice character: {new_character_name}")
            return True
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return False
    
    def get_characters_by_tags(self, tags: List[str]) -> List[VoiceCharacter]:
        """Get characters matching tags"""
        matching_characters = []
        
        for character in self.voice_characters.values():
            if any(tag in character.tags for tag in tags):
                matching_characters.append(character)
        
        return matching_characters
    
    def get_characters_by_language(self, language: str) -> List[VoiceCharacter]:
        """Get characters by language"""
        return [char for char in self.voice_characters.values() 
                if char.language == language or char.language == "auto"]
    
    def get_available_characters(self) -> List[str]:
        """Get list of available character names"""
        return list(self.voice_characters.keys())
    
    def get_character_info(self, character_name: str) -> Optional[Dict]:
        """Get detailed character information"""
        if character_name in self.voice_characters:
            character = self.voice_characters[character_name]
            return {
                "name": character.name,
                "display_name": character.display_name,
                "description": character.description,
                "gender": character.gender,
                "age_range": character.age_range,
                "language": character.language,
                "tags": character.tags,
                "has_sample": character.voice_sample_path is not None,
                "sample_count": len(character.reference_samples)
            }
        return None
    
    def save_characters(self, file_path: str) -> bool:
        """Save characters to file"""
        try:
            data = {}
            for name, character in self.voice_characters.items():
                data[name] = asdict(character)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Characters saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save characters: {e}")
            return False
    
    def load_characters(self, file_path: str) -> bool:
        """Load characters from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for name, character_data in data.items():
                character = VoiceCharacter(**character_data)
                self.voice_characters[name] = character
            
            logger.info(f"Characters loaded from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load characters: {e}")
            return False
    
    def validate_voice_samples(self) -> Dict[str, bool]:
        """Validate that voice sample files exist"""
        validation_results = {}
        
        for name, character in self.voice_characters.items():
            if character.voice_sample_path:
                validation_results[name] = os.path.exists(character.voice_sample_path)
            else:
                validation_results[name] = True  # No sample required
        
        return validation_results

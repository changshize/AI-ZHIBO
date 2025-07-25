#!/usr/bin/env python3
"""
AI Voice Streaming Host - Quick Demo Script
AI语音直播主播 - 快速演示脚本

A simple demo to test the AI voice streaming system without full setup
"""
import asyncio
import logging
import sys
import time
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Try to import our modules
try:
    from src.config import settings
    from src.voice_engine import VoiceManager
    from src.characters import PersonalityManager, ASMRManager
    from src.language import TextProcessor
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.error("Please make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


class SimpleDemo:
    """Simple demonstration of AI voice capabilities"""
    
    def __init__(self):
        self.voice_manager = VoiceManager()
        self.personality_manager = PersonalityManager()
        self.asmr_manager = ASMRManager()
        self.text_processor = TextProcessor()
        
        self.demo_texts = {
            "chinese": [
                "大家好！我是你们的AI虚拟主播！",
                "今天天气真不错，大家心情怎么样？",
                "谢谢大家的支持，我会继续努力的！",
                "有什么想聊的话题吗？我很想听听大家的想法。"
            ],
            "english": [
                "Hello everyone! I'm your AI virtual host!",
                "Welcome to my stream! How is everyone doing today?",
                "Thank you so much for your support!",
                "What would you like to talk about today?"
            ],
            "asmr": [
                "轻轻地... 闭上眼睛... 听我的声音...",
                "慢慢地... 深呼吸... 放松你的身体...",
                "Let the sound wash over you... so peaceful...",
                "Gently... just relax... everything is calm..."
            ]
        }
    
    async def initialize(self) -> bool:
        """Initialize the demo system"""
        try:
            logger.info("🎤 Initializing AI Voice Demo...")
            
            # Try to initialize voice manager
            if not self.voice_manager.initialize():
                logger.warning("⚠️ Voice manager initialization failed - running in text-only mode")
                return False
            
            logger.info("✅ Demo system initialized!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo initialization failed: {e}")
            return False
    
    async def run_personality_demo(self):
        """Demonstrate different personalities"""
        logger.info("🎭 === Personality Demo ===")
        
        personalities = ["cute_girl", "asmr_girl", "energetic_girl", "shy_girl"]
        
        for personality in personalities:
            try:
                logger.info(f"👤 Testing personality: {personality}")
                
                # Switch personality
                self.personality_manager.set_personality(personality)
                current = self.personality_manager.get_current_personality()
                
                if current:
                    logger.info(f"   Name: {current.name}")
                    logger.info(f"   Description: {current.description}")
                    logger.info(f"   Voice settings: pitch={current.voice_pitch:.1f}, speed={current.voice_speed:.1f}")
                    
                    # Get voice profile
                    voice_profile = self.personality_manager.get_voice_profile()
                    logger.info(f"   Voice profile: {voice_profile.name}")
                    
                    # Generate sample text
                    sample_text = self.personality_manager.get_response_text("greeting")
                    logger.info(f"   Sample: {sample_text}")
                    
                    # Try to synthesize if voice manager is available
                    if self.voice_manager.is_initialized:
                        logger.info("   🎵 Synthesizing audio...")
                        audio = self.voice_manager.synthesize(
                            text=sample_text,
                            voice_profile_name=voice_profile.name,
                            mode="batch"
                        )
                        if audio is not None:
                            logger.info("   ✅ Audio synthesis successful!")
                        else:
                            logger.warning("   ⚠️ Audio synthesis failed")
                    
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"   ❌ Error testing {personality}: {e}")
    
    async def run_asmr_demo(self):
        """Demonstrate ASMR modes"""
        logger.info("🎵 === ASMR Demo ===")
        
        asmr_modes = ["gentle_whisper", "personal_attention", "rain_nature", "tapping_sounds"]
        
        for mode in asmr_modes:
            try:
                logger.info(f"🎭 Testing ASMR mode: {mode}")
                
                # Switch ASMR mode
                self.asmr_manager.set_asmr_mode(mode)
                current = self.asmr_manager.get_current_mode()
                
                if current:
                    logger.info(f"   Name: {current.name}")
                    logger.info(f"   Description: {current.description}")
                    logger.info(f"   Mood: {current.mood}")
                    logger.info(f"   Voice settings: pitch={current.voice_pitch:.1f}, speed={current.voice_speed:.1f}")
                    
                    # Generate ASMR text
                    asmr_text = self.asmr_manager.generate_asmr_text()
                    logger.info(f"   Sample: {asmr_text}")
                    
                    # Get voice profile
                    voice_profile = self.asmr_manager.get_asmr_voice_profile()
                    logger.info(f"   Voice profile: {voice_profile.name}")
                    
                    await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"   ❌ Error testing {mode}: {e}")
    
    async def run_text_processing_demo(self):
        """Demonstrate text processing"""
        logger.info("📝 === Text Processing Demo ===")
        
        test_texts = [
            "Hello! 😊 How are you today? I'm so excited!!!",
            "大家好！😄 今天天气真不错～ 心情超级棒！！！",
            "Let's go!!! 🔥🔥🔥 This is amazing!",
            "轻轻地... 慢慢来... 放松一下... 😴💤"
        ]
        
        for text in test_texts:
            try:
                logger.info(f"📝 Original: {text}")
                
                # Process text
                processed = self.text_processor.process_text(text)
                logger.info(f"   Processed: {processed}")
                
                # Extract emotions
                emotions = self.text_processor.extract_emotions(text)
                if emotions:
                    logger.info(f"   Emotions: {', '.join(emotions)}")
                
                # Detect language
                is_chinese = self.text_processor._is_chinese(text)
                is_english = self.text_processor._is_english(text)
                logger.info(f"   Language: {'Chinese' if is_chinese else 'English' if is_english else 'Mixed'}")
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"   ❌ Error processing text: {e}")
    
    async def run_interactive_demo(self):
        """Run interactive demo"""
        logger.info("💬 === Interactive Demo ===")
        logger.info("Type messages to test the system. Commands:")
        logger.info("  !personality <name> - Switch personality")
        logger.info("  !asmr <mode> - Switch ASMR mode")
        logger.info("  !quit - Exit demo")
        
        while True:
            try:
                user_input = input("\n📝 Enter message: ").strip()
                
                if user_input.lower() in ['!quit', 'quit', 'exit']:
                    break
                
                # Handle commands
                if user_input.startswith('!'):
                    await self._handle_command(user_input)
                    continue
                
                if user_input:
                    # Process text
                    processed_text = self.text_processor.process_text(user_input)
                    logger.info(f"📝 Processed: {processed_text}")
                    
                    # Get personality response
                    personality_response = self.personality_manager.get_response_text("general", processed_text)
                    logger.info(f"👤 Personality response: {personality_response}")
                    
                    # Get ASMR enhancement if active
                    if self.asmr_manager.is_asmr_active():
                        asmr_response = self.asmr_manager.generate_asmr_text(personality_response)
                        logger.info(f"🎵 ASMR enhanced: {asmr_response}")
                    
                    # Try synthesis if available
                    if self.voice_manager.is_initialized:
                        logger.info("🎵 Synthesizing...")
                        # This would normally play audio
                        logger.info("✅ (Audio would play here)")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Interactive demo error: {e}")
    
    async def _handle_command(self, command: str):
        """Handle demo commands"""
        try:
            parts = command[1:].split()
            cmd = parts[0].lower()
            
            if cmd == "personality" and len(parts) > 1:
                personality = parts[1]
                available = self.personality_manager.get_available_personalities()
                if personality in available:
                    self.personality_manager.set_personality(personality)
                    logger.info(f"✅ Switched to personality: {personality}")
                else:
                    logger.info(f"❌ Available personalities: {', '.join(available)}")
            
            elif cmd == "asmr" and len(parts) > 1:
                asmr_mode = parts[1]
                available = self.asmr_manager.get_available_modes()
                if asmr_mode in available:
                    self.asmr_manager.set_asmr_mode(asmr_mode)
                    logger.info(f"✅ Switched to ASMR mode: {asmr_mode}")
                else:
                    logger.info(f"❌ Available ASMR modes: {', '.join(available)}")
            
            else:
                logger.info("❌ Unknown command")
                
        except Exception as e:
            logger.error(f"❌ Command error: {e}")
    
    def cleanup(self):
        """Cleanup demo resources"""
        try:
            if hasattr(self.voice_manager, 'cleanup'):
                self.voice_manager.cleanup()
            logger.info("✅ Demo cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")


async def main():
    """Main demo function"""
    demo = SimpleDemo()
    
    try:
        # Initialize
        voice_available = await demo.initialize()
        
        if not voice_available:
            logger.warning("⚠️ Running in limited mode (text processing only)")
        
        # Run demos
        await demo.run_text_processing_demo()
        await demo.run_personality_demo()
        await demo.run_asmr_demo()
        
        # Interactive demo
        logger.info("\n🎮 Starting interactive demo...")
        await demo.run_interactive_demo()
        
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo error: {e}")
    finally:
        demo.cleanup()
    
    logger.info("👋 Demo completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

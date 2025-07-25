#!/usr/bin/env python3
"""
AI Voice Streaming Host - Simple Demo (No TTS Required)
AI语音直播主播 - 简单演示（无需TTS库）

A demonstration of the core functionality without requiring TTS models
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

def print_banner():
    """Print project banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                🎤 AI Voice Streaming Host 🎤                 ║
║                   AI语音直播主播系统                          ║
║                                                              ║
║  🎯 Features: Multi-personality AI voice streaming          ║
║  🌍 Languages: Chinese & English                            ║
║  🎭 Characters: Cute, ASMR, Energetic, Shy                  ║
║  📱 Platform: 抖音 (Douyin) Live Streaming                   ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def demo_text_processing():
    """Demonstrate text processing capabilities"""
    logger.info("🔤 === Text Processing Demo ===")
    
    try:
        from src.language import TextProcessor, EmotionDetector, MultilingualHandler
        
        processor = TextProcessor()
        emotion_detector = EmotionDetector()
        multilingual = MultilingualHandler()
        
        test_cases = [
            {
                "text": "大家好！我是你们的AI虚拟主播！😊",
                "description": "Chinese greeting with emoji"
            },
            {
                "text": "Hello everyone! Welcome to my stream! 🎉",
                "description": "English greeting with excitement"
            },
            {
                "text": "轻轻地... 闭上眼睛... 听我的声音... 💤",
                "description": "ASMR Chinese text"
            },
            {
                "text": "Let's play some games together! So exciting! 🎮🔥",
                "description": "Gaming content with energy"
            },
            {
                "text": "那个... 大家好... 我有点紧张... 😳",
                "description": "Shy personality expression"
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {case['description']}")
            print(f"   Original: {case['text']}")
            
            # Process text
            processed = processor.process_text(case['text'])
            print(f"   Processed: {processed}")
            
            # Detect emotions
            emotions = emotion_detector.detect_emotions(case['text'])
            if emotions:
                emotion_str = ", ".join([f"{emotion.value}({conf:.2f})" for emotion, conf in emotions[:3]])
                print(f"   Emotions: {emotion_str}")
            
            # Detect language
            language, confidence = multilingual.detect_language(case['text'])
            print(f"   Language: {language.value} (confidence: {confidence:.2f})")
            
            await asyncio.sleep(0.5)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Text processing demo failed: {e}")
        return False

async def demo_personality_system():
    """Demonstrate personality system"""
    logger.info("🎭 === Personality System Demo ===")
    
    try:
        from src.characters import PersonalityManager
        
        manager = PersonalityManager()
        personalities = manager.get_available_personalities()
        
        print(f"\n🎯 Available Personalities: {len(personalities)}")
        
        for personality_name in personalities:
            print(f"\n👤 Testing Personality: {personality_name}")
            
            # Switch personality
            success = manager.set_personality(personality_name)
            if success:
                current = manager.get_current_personality()
                print(f"   Name: {current.name}")
                print(f"   Description: {current.description}")
                print(f"   Voice Settings: pitch={current.voice_pitch:.1f}, speed={current.voice_speed:.1f}")
                print(f"   Emotion Tendency: {current.emotion_tendency.value}")
                
                # Generate sample responses
                contexts = ["greeting", "thanks", "excitement"]
                for context in contexts:
                    response = manager.get_response_text(context)
                    print(f"   {context.title()}: {response}")
                
                # Get voice profile
                voice_profile = manager.get_voice_profile()
                print(f"   Voice Profile: {voice_profile.name} (pitch={voice_profile.pitch:.1f})")
            
            await asyncio.sleep(1)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Personality demo failed: {e}")
        return False

async def demo_asmr_system():
    """Demonstrate ASMR system"""
    logger.info("🎵 === ASMR System Demo ===")
    
    try:
        from src.characters import ASMRManager
        
        manager = ASMRManager()
        modes = manager.get_available_modes()
        
        print(f"\n🎯 Available ASMR Modes: {len(modes)}")
        
        for mode_name in modes:
            print(f"\n🎭 Testing ASMR Mode: {mode_name}")
            
            # Switch ASMR mode
            success = manager.set_asmr_mode(mode_name)
            if success:
                current = manager.get_current_mode()
                print(f"   Name: {current.name}")
                print(f"   Description: {current.description}")
                print(f"   Mood: {current.mood.value}")
                print(f"   Voice Settings: pitch={current.voice_pitch:.1f}, speed={current.voice_speed:.1f}")
                
                # Generate ASMR text
                sample_texts = [
                    "Hello, welcome to my ASMR session",
                    "大家好，欢迎来到我的ASMR直播",
                    "Let's relax together"
                ]
                
                for text in sample_texts:
                    asmr_text = manager.generate_asmr_text(text)
                    print(f"   Enhanced: {asmr_text}")
                
                # Get voice profile
                voice_profile = manager.get_asmr_voice_profile()
                print(f"   Voice Profile: {voice_profile.name}")
            
            await asyncio.sleep(1)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ASMR demo failed: {e}")
        return False

async def demo_interactive_session():
    """Interactive demonstration"""
    logger.info("💬 === Interactive Demo ===")
    
    try:
        from src.characters import PersonalityManager, ASMRManager
        from src.language import TextProcessor, EmotionDetector
        
        personality_manager = PersonalityManager()
        asmr_manager = ASMRManager()
        text_processor = TextProcessor()
        emotion_detector = EmotionDetector()
        
        print("\n🎮 Interactive AI Voice Host Demo")
        print("Commands:")
        print("  !personality <name> - Switch personality")
        print("  !asmr <mode> - Switch ASMR mode")
        print("  !list - Show available options")
        print("  !quit - Exit demo")
        print("\nType a message to see how the AI processes it!")
        
        # Set default personality
        personality_manager.set_personality("cute_girl")
        
        while True:
            try:
                user_input = input("\n📝 Enter message: ").strip()
                
                if user_input.lower() in ['!quit', 'quit', 'exit']:
                    break
                
                # Handle commands
                if user_input.startswith('!'):
                    await handle_command(user_input, personality_manager, asmr_manager)
                    continue
                
                if user_input:
                    print(f"\n🔄 Processing: {user_input}")
                    
                    # Process text
                    processed = text_processor.process_text(user_input)
                    print(f"📝 Processed Text: {processed}")
                    
                    # Detect emotions
                    emotions = emotion_detector.detect_emotions(user_input)
                    if emotions:
                        emotion_str = ", ".join([f"{e.value}" for e, _ in emotions[:2]])
                        print(f"😊 Detected Emotions: {emotion_str}")
                    
                    # Get personality response
                    personality_response = personality_manager.get_response_text("general", processed)
                    print(f"👤 Personality Response: {personality_response}")
                    
                    # Apply ASMR if active
                    if asmr_manager.is_asmr_active():
                        asmr_response = asmr_manager.generate_asmr_text(personality_response)
                        print(f"🎵 ASMR Enhanced: {asmr_response}")
                    
                    # Show current settings
                    current_personality = personality_manager.get_current_personality()
                    current_asmr = asmr_manager.get_current_mode()
                    
                    settings_info = f"Settings: {current_personality.name if current_personality else 'None'}"
                    if current_asmr:
                        settings_info += f" + {current_asmr.name}"
                    print(f"⚙️ {settings_info}")
                    
                    print("🎤 [In real application, this would be synthesized to speech]")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Interactive demo error: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Interactive demo failed: {e}")
        return False

async def handle_command(command: str, personality_manager, asmr_manager):
    """Handle demo commands"""
    try:
        parts = command[1:].split()
        cmd = parts[0].lower()
        
        if cmd == "personality" and len(parts) > 1:
            personality = parts[1]
            available = personality_manager.get_available_personalities()
            if personality in available:
                personality_manager.set_personality(personality)
                print(f"✅ Switched to personality: {personality}")
            else:
                print(f"❌ Available personalities: {', '.join(available)}")
        
        elif cmd == "asmr" and len(parts) > 1:
            asmr_mode = parts[1]
            available = asmr_manager.get_available_modes()
            if asmr_mode in available:
                asmr_manager.set_asmr_mode(asmr_mode)
                print(f"✅ Switched to ASMR mode: {asmr_mode}")
            else:
                print(f"❌ Available ASMR modes: {', '.join(available)}")
        
        elif cmd == "list":
            personalities = personality_manager.get_available_personalities()
            asmr_modes = asmr_manager.get_available_modes()
            print(f"👤 Personalities: {', '.join(personalities)}")
            print(f"🎵 ASMR Modes: {', '.join(asmr_modes)}")
        
        else:
            print("❌ Unknown command. Available: !personality, !asmr, !list, !quit")
            
    except Exception as e:
        logger.error(f"❌ Command error: {e}")

async def main():
    """Main demo function"""
    print_banner()
    
    logger.info("🚀 Starting AI Voice Streaming Host Demo...")
    logger.info("📝 Note: This demo shows text processing without actual voice synthesis")
    
    try:
        # Run component demos
        demos = [
            ("Text Processing", demo_text_processing),
            ("Personality System", demo_personality_system),
            ("ASMR System", demo_asmr_system),
        ]
        
        for demo_name, demo_func in demos:
            logger.info(f"\n🎬 Running {demo_name} Demo...")
            success = await demo_func()
            if success:
                logger.info(f"✅ {demo_name} demo completed successfully")
            else:
                logger.warning(f"⚠️ {demo_name} demo had issues")
            
            await asyncio.sleep(1)
        
        # Interactive demo
        logger.info("\n🎮 Starting Interactive Demo...")
        await demo_interactive_session()
        
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo error: {e}")
    
    logger.info("👋 Demo completed! Thank you for trying AI Voice Streaming Host!")
    logger.info("🎤 For full voice synthesis, install TTS models and run: python main.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

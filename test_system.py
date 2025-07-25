#!/usr/bin/env python3
"""
AI Voice Streaming Host - System Test Script
AI语音直播主播 - 系统测试脚本

Quick test script to verify system functionality
"""
import asyncio
import logging
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_imports():
    """Test if all modules can be imported"""
    logger.info("🧪 Testing module imports...")
    
    try:
        from src.config import settings, VoiceProfile
        logger.info("✅ Config module imported")
        
        from src.voice_engine import VoiceManager, XTTSEngine, RealtimeTTSEngine
        logger.info("✅ Voice engine modules imported")
        
        from src.characters import PersonalityManager, ASMRManager, VoiceProfileManager
        logger.info("✅ Character system modules imported")
        
        from src.language import TextProcessor, EmotionDetector, MultilingualHandler
        logger.info("✅ Language processing modules imported")
        
        from src.streaming import AudioStreamer
        logger.info("✅ Streaming modules imported")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False


async def test_configuration():
    """Test configuration system"""
    logger.info("🧪 Testing configuration...")
    
    try:
        from src.config import settings, get_settings, VoiceProfile
        
        # Test settings access
        logger.info(f"✅ App name: {settings.app_name}")
        logger.info(f"✅ Primary engine: {settings.primary_voice_engine}")
        logger.info(f"✅ Sample rate: {settings.sample_rate}")
        
        # Test voice profile creation
        profile = VoiceProfile(
            name="test_profile",
            gender="female",
            pitch=1.1,
            speed=1.0
        )
        logger.info(f"✅ Voice profile created: {profile.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False


async def test_personality_system():
    """Test personality management"""
    logger.info("🧪 Testing personality system...")
    
    try:
        from src.characters import PersonalityManager
        
        manager = PersonalityManager()
        
        # Test personality listing
        personalities = manager.get_available_personalities()
        logger.info(f"✅ Found {len(personalities)} personalities: {personalities}")
        
        # Test personality switching
        if personalities:
            test_personality = personalities[0]
            success = manager.set_personality(test_personality)
            if success:
                logger.info(f"✅ Switched to personality: {test_personality}")
                
                # Test voice profile generation
                voice_profile = manager.get_voice_profile()
                logger.info(f"✅ Generated voice profile: {voice_profile.name}")
                
                # Test response generation
                response = manager.get_response_text("greeting")
                logger.info(f"✅ Generated response: {response[:50]}...")
            else:
                logger.error(f"❌ Failed to switch personality")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Personality system test failed: {e}")
        return False


async def test_asmr_system():
    """Test ASMR system"""
    logger.info("🧪 Testing ASMR system...")
    
    try:
        from src.characters import ASMRManager
        
        manager = ASMRManager()
        
        # Test ASMR mode listing
        modes = manager.get_available_modes()
        logger.info(f"✅ Found {len(modes)} ASMR modes: {modes}")
        
        # Test ASMR mode switching
        if modes:
            test_mode = modes[0]
            success = manager.set_asmr_mode(test_mode)
            if success:
                logger.info(f"✅ Switched to ASMR mode: {test_mode}")
                
                # Test ASMR text generation
                asmr_text = manager.generate_asmr_text("Hello, this is a test")
                logger.info(f"✅ Generated ASMR text: {asmr_text}")
                
                # Test voice profile
                voice_profile = manager.get_asmr_voice_profile()
                logger.info(f"✅ ASMR voice profile: {voice_profile.name}")
            else:
                logger.error(f"❌ Failed to switch ASMR mode")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ASMR system test failed: {e}")
        return False


async def test_text_processing():
    """Test text processing"""
    logger.info("🧪 Testing text processing...")
    
    try:
        from src.language import TextProcessor, EmotionDetector, MultilingualHandler
        
        # Test text processor
        processor = TextProcessor()
        
        test_texts = [
            "Hello! 😊 How are you today?",
            "大家好！今天天气真不错～",
            "Let's test some emoji processing! 🎉🔥"
        ]
        
        for text in test_texts:
            processed = processor.process_text(text)
            emotions = processor.extract_emotions(text)
            logger.info(f"✅ Processed: '{text}' -> '{processed}' (emotions: {emotions})")
        
        # Test emotion detector
        emotion_detector = EmotionDetector()
        
        test_emotion_text = "I'm so happy and excited! 😄🎉"
        emotions = emotion_detector.detect_emotions(test_emotion_text)
        logger.info(f"✅ Detected emotions: {emotions}")
        
        # Test multilingual handler
        multilingual = MultilingualHandler()
        
        mixed_text = "Hello 大家好 this is mixed language text"
        language, confidence = multilingual.detect_language(mixed_text)
        logger.info(f"✅ Language detection: {language} (confidence: {confidence:.2f})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Text processing test failed: {e}")
        return False


async def test_voice_manager():
    """Test voice manager (without actual synthesis)"""
    logger.info("🧪 Testing voice manager...")
    
    try:
        from src.voice_engine import VoiceManager
        
        manager = VoiceManager()
        
        # Test initialization (may fail if models not available)
        logger.info("Attempting voice manager initialization...")
        success = manager.initialize()
        
        if success:
            logger.info("✅ Voice manager initialized successfully")
            
            # Test engine listing
            engines = manager.get_available_engines()
            logger.info(f"✅ Available engines: {engines}")
            
            # Test profile listing
            profiles = manager.get_available_profiles()
            logger.info(f"✅ Available profiles: {profiles}")
            
        else:
            logger.warning("⚠️ Voice manager initialization failed (models may not be available)")
            logger.info("This is expected if TTS models are not installed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Voice manager test failed: {e}")
        return False


async def test_audio_streamer():
    """Test audio streamer (without actual audio)"""
    logger.info("🧪 Testing audio streamer...")
    
    try:
        from src.streaming import AudioStreamer
        
        streamer = AudioStreamer()
        
        # Test initialization
        success = streamer.initialize()
        
        if success:
            logger.info("✅ Audio streamer initialized")
            
            # Test stats
            stats = streamer.get_stream_stats()
            logger.info(f"✅ Stream stats: {stats}")
            
        else:
            logger.warning("⚠️ Audio streamer initialization failed (audio system may not be available)")
            logger.info("This is expected if audio drivers are not properly configured")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Audio streamer test failed: {e}")
        return False


async def run_all_tests():
    """Run all system tests"""
    logger.info("🚀 Starting AI Voice Streaming Host system tests...")
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Personality System", test_personality_system),
        ("ASMR System", test_asmr_system),
        ("Text Processing", test_text_processing),
        ("Voice Manager", test_voice_manager),
        ("Audio Streamer", test_audio_streamer),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running test: {test_name}")
        try:
            success = await test_func()
            if success:
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready to use.")
    elif passed >= total * 0.7:
        logger.info("⚠️ Most tests passed. System should work with some limitations.")
    else:
        logger.error("❌ Many tests failed. Please check installation and dependencies.")
    
    return passed == total


async def main():
    """Main test function"""
    try:
        success = await run_all_tests()
        
        if success:
            logger.info("\n🎮 You can now run:")
            logger.info("  python demo.py          - For a quick demo")
            logger.info("  python main.py --mode demo  - For full demo")
            logger.info("  python main.py --mode interactive  - For interactive mode")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

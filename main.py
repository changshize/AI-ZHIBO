"""
AI Voice Streaming Host - Main Application
AI语音直播主播 - 主程序

A sophisticated AI-powered voice streaming system for live platforms like 抖音 (Douyin)
支持多语言、多个性、ASMR模式的AI虚拟主播系统
"""
import asyncio
import logging
import signal
import sys
import time
from typing import Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import our modules
from src.config import settings, get_settings
from src.voice_engine import VoiceManager
from src.characters import PersonalityManager, ASMRManager
from src.streaming import AudioStreamer


class AIVoiceStreamingHost:
    """Main AI Voice Streaming Host application"""
    
    def __init__(self):
        self.voice_manager = VoiceManager()
        self.personality_manager = PersonalityManager()
        self.asmr_manager = ASMRManager()
        self.audio_streamer = AudioStreamer()
        
        self.is_running = False
        self.current_session = None
        
        # Performance metrics
        self.start_time = None
        self.total_messages = 0
        self.total_audio_generated = 0
    
    async def initialize(self) -> bool:
        """Initialize all components"""
        try:
            logger.info("🎤 Initializing AI Voice Streaming Host...")
            logger.info(f"📱 Target Platform: {settings.streaming_platform}")
            logger.info(f"🗣️ Primary Engine: {settings.primary_voice_engine}")
            
            # Initialize voice manager
            if not self.voice_manager.initialize():
                logger.error("❌ Failed to initialize voice manager")
                return False
            
            # Initialize audio streamer
            if not self.audio_streamer.initialize():
                logger.error("❌ Failed to initialize audio streamer")
                return False
            
            # Set default personality
            self.personality_manager.set_personality("cute_girl")
            
            logger.info("✅ AI Voice Streaming Host initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def start_streaming(self) -> bool:
        """Start the streaming session"""
        try:
            logger.info("🚀 Starting streaming session...")
            
            # Start audio output stream
            if not self.audio_streamer.start_output_stream():
                logger.error("❌ Failed to start audio stream")
                return False
            
            self.is_running = True
            self.start_time = time.time()
            
            logger.info("🎵 Streaming session started!")
            logger.info("💡 Ready to generate AI voice content!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start streaming: {e}")
            return False
    
    async def synthesize_and_stream(
        self,
        text: str,
        personality: Optional[str] = None,
        asmr_mode: Optional[str] = None,
        language: str = "auto"
    ) -> bool:
        """Synthesize text and stream audio"""
        try:
            # Switch personality if specified
            if personality:
                self.personality_manager.set_personality(personality)
            
            # Switch ASMR mode if specified
            if asmr_mode:
                self.asmr_manager.set_asmr_mode(asmr_mode)
                # Enhance text with ASMR elements
                text = self.asmr_manager.generate_asmr_text(text)
                # Use ASMR voice profile
                voice_profile = self.asmr_manager.get_asmr_voice_profile()
            else:
                # Use personality voice profile
                voice_profile = self.personality_manager.get_voice_profile()
            
            # Enhance text with personality
            enhanced_text = self.personality_manager.get_response_text("general", text)
            
            logger.info(f"🎯 Synthesizing: {enhanced_text[:50]}...")
            logger.info(f"👤 Personality: {self.personality_manager.current_personality.name if self.personality_manager.current_personality else 'Default'}")
            logger.info(f"🎵 Voice Profile: pitch={voice_profile.pitch:.1f}, speed={voice_profile.speed:.1f}")
            
            # Synthesize audio using streaming mode
            audio_generator = self.voice_manager.synthesize(
                text=enhanced_text,
                voice_profile_name=voice_profile.name,
                language=language,
                mode="streaming"
            )
            
            if audio_generator:
                # Stream the audio
                self.audio_streamer.stream_audio_generator(audio_generator)
                self.total_messages += 1
                logger.info("✅ Audio synthesis and streaming completed")
                return True
            else:
                logger.error("❌ Failed to generate audio")
                return False
                
        except Exception as e:
            logger.error(f"❌ Synthesis and streaming failed: {e}")
            return False
    
    async def demo_session(self):
        """Run a demonstration session"""
        logger.info("🎭 Starting demonstration session...")
        
        # Demo messages in different personalities and modes
        demo_scenarios = [
            {
                "text": "大家好！欢迎来到我的直播间！今天我们一起聊天吧！",
                "personality": "cute_girl",
                "asmr_mode": None,
                "language": "zh"
            },
            {
                "text": "Hello everyone! Welcome to my stream! Let's have some fun today!",
                "personality": "energetic_girl", 
                "asmr_mode": None,
                "language": "en"
            },
            {
                "text": "轻轻地... 闭上眼睛... 让我的声音陪伴你入睡...",
                "personality": "asmr_girl",
                "asmr_mode": "gentle_whisper",
                "language": "zh"
            },
            {
                "text": "那个... 大家好... 我有点紧张... 请多多关照...",
                "personality": "shy_girl",
                "asmr_mode": None,
                "language": "zh"
            },
            {
                "text": "Listen to the gentle rain... so peaceful and relaxing...",
                "personality": "asmr_girl",
                "asmr_mode": "rain_nature",
                "language": "en"
            }
        ]
        
        for i, scenario in enumerate(demo_scenarios, 1):
            logger.info(f"🎬 Demo scenario {i}/{len(demo_scenarios)}")
            
            await self.synthesize_and_stream(
                text=scenario["text"],
                personality=scenario["personality"],
                asmr_mode=scenario["asmr_mode"],
                language=scenario["language"]
            )
            
            # Wait between scenarios
            await asyncio.sleep(3)
        
        logger.info("🎭 Demonstration session completed!")
    
    async def interactive_session(self):
        """Run interactive session with user input"""
        logger.info("💬 Starting interactive session...")
        logger.info("💡 Type your message and press Enter. Type 'quit' to exit.")
        logger.info("💡 Commands: !personality <name>, !asmr <mode>, !stats")
        
        while self.is_running:
            try:
                # Get user input (in a real application, this would come from chat/API)
                user_input = input("\n📝 Enter message: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                # Handle commands
                if user_input.startswith('!'):
                    await self.handle_command(user_input)
                    continue
                
                if user_input:
                    await self.synthesize_and_stream(user_input)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Interactive session error: {e}")
    
    async def handle_command(self, command: str):
        """Handle user commands"""
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
            
            elif cmd == "stats":
                await self.show_stats()
            
            elif cmd == "help":
                logger.info("📋 Available commands:")
                logger.info("  !personality <name> - Switch personality")
                logger.info("  !asmr <mode> - Switch ASMR mode")
                logger.info("  !stats - Show statistics")
                logger.info("  !help - Show this help")
            
            else:
                logger.info("❌ Unknown command. Type !help for available commands.")
                
        except Exception as e:
            logger.error(f"❌ Command handling error: {e}")
    
    async def show_stats(self):
        """Show application statistics"""
        try:
            uptime = time.time() - self.start_time if self.start_time else 0
            stream_stats = self.audio_streamer.get_stream_stats()
            
            logger.info("📊 === AI Voice Streaming Host Statistics ===")
            logger.info(f"⏱️  Uptime: {uptime:.1f} seconds")
            logger.info(f"💬 Total messages: {self.total_messages}")
            logger.info(f"🎵 Streaming: {stream_stats['is_streaming']}")
            logger.info(f"📊 Queue size: {stream_stats['queue_size']}")
            logger.info(f"⚡ Latency: {stream_stats['latency_ms']:.1f}ms")
            logger.info(f"🔧 Sample rate: {stream_stats['sample_rate']}Hz")
            logger.info(f"👤 Current personality: {self.personality_manager.current_personality.name if self.personality_manager.current_personality else 'None'}")
            logger.info(f"🎭 ASMR mode: {self.asmr_manager.current_mode.name if self.asmr_manager.current_mode else 'None'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to show stats: {e}")
    
    def stop(self):
        """Stop the application"""
        logger.info("🛑 Stopping AI Voice Streaming Host...")
        self.is_running = False
        
        # Cleanup components
        self.audio_streamer.cleanup()
        self.voice_manager.cleanup()
        
        logger.info("✅ Application stopped successfully")


async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="AI Voice Streaming Host")
    parser.add_argument("--mode", choices=["demo", "interactive"], default="demo",
                       help="Run mode: demo or interactive")
    parser.add_argument("--personality", default="cute_girl",
                       help="Initial personality")
    parser.add_argument("--platform", default="douyin",
                       help="Streaming platform")
    
    args = parser.parse_args()
    
    # Create application instance
    app = AIVoiceStreamingHost()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info("🛑 Received interrupt signal")
        app.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize application
        if not await app.initialize():
            logger.error("❌ Failed to initialize application")
            return 1
        
        # Start streaming
        if not await app.start_streaming():
            logger.error("❌ Failed to start streaming")
            return 1
        
        # Run based on mode
        if args.mode == "demo":
            await app.demo_session()
        elif args.mode == "interactive":
            await app.interactive_session()
        
        # Show final stats
        await app.show_stats()
        
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        return 1
    finally:
        app.stop()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

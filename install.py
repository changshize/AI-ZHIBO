#!/usr/bin/env python3
"""
AI Voice Streaming Host - Installation Script
AI语音直播主播 - 安装脚本

Automated installation and setup script
"""
import os
import sys
import subprocess
import platform
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Installer:
    """Installation manager for AI Voice Streaming Host"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        self.project_root = Path(__file__).parent
        
    def check_requirements(self) -> bool:
        """Check system requirements"""
        logger.info("🔍 Checking system requirements...")
        
        # Check Python version
        if self.python_version < (3, 8):
            logger.error("❌ Python 3.8+ required. Current version: {}.{}.{}".format(
                self.python_version.major, 
                self.python_version.minor, 
                self.python_version.micro
            ))
            return False
        
        logger.info(f"✅ Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            logger.info("✅ pip is available")
        except subprocess.CalledProcessError:
            logger.error("❌ pip is not available")
            return False
        
        return True
    
    def install_system_dependencies(self) -> bool:
        """Install system-level dependencies"""
        logger.info("📦 Installing system dependencies...")
        
        try:
            if self.system == "linux":
                return self._install_linux_deps()
            elif self.system == "darwin":  # macOS
                return self._install_macos_deps()
            elif self.system == "windows":
                return self._install_windows_deps()
            else:
                logger.warning(f"⚠️ Unsupported system: {self.system}")
                return True  # Continue anyway
                
        except Exception as e:
            logger.error(f"❌ System dependency installation failed: {e}")
            return False
    
    def _install_linux_deps(self) -> bool:
        """Install Linux dependencies"""
        try:
            # Check if we can use apt
            subprocess.run(["which", "apt-get"], check=True, capture_output=True)
            
            logger.info("Installing audio dependencies...")
            subprocess.run([
                "sudo", "apt-get", "update"
            ], check=True)
            
            subprocess.run([
                "sudo", "apt-get", "install", "-y",
                "portaudio19-dev", "python3-dev", "build-essential",
                "ffmpeg", "libsndfile1", "libasound2-dev"
            ], check=True)
            
            logger.info("✅ Linux dependencies installed")
            return True
            
        except subprocess.CalledProcessError:
            logger.warning("⚠️ Could not install system dependencies automatically")
            logger.info("Please install manually: portaudio19-dev python3-dev build-essential ffmpeg")
            return True  # Continue anyway
        except FileNotFoundError:
            logger.warning("⚠️ apt-get not found, skipping system dependencies")
            return True
    
    def _install_macos_deps(self) -> bool:
        """Install macOS dependencies"""
        try:
            # Check if brew is available
            subprocess.run(["which", "brew"], check=True, capture_output=True)
            
            logger.info("Installing audio dependencies with Homebrew...")
            subprocess.run(["brew", "install", "portaudio", "ffmpeg"], check=True)
            
            logger.info("✅ macOS dependencies installed")
            return True
            
        except subprocess.CalledProcessError:
            logger.warning("⚠️ Could not install system dependencies automatically")
            logger.info("Please install Homebrew and run: brew install portaudio ffmpeg")
            return True
        except FileNotFoundError:
            logger.warning("⚠️ Homebrew not found, skipping system dependencies")
            return True
    
    def _install_windows_deps(self) -> bool:
        """Install Windows dependencies"""
        logger.info("⚠️ Windows system dependencies need manual installation:")
        logger.info("1. Install Microsoft Visual C++ Build Tools")
        logger.info("2. Install FFmpeg and add to PATH")
        logger.info("3. Consider using conda for easier dependency management")
        return True
    
    def create_directories(self) -> bool:
        """Create necessary directories"""
        logger.info("📁 Creating directories...")
        
        directories = [
            "models",
            "voices", 
            "cache",
            "logs",
            "config"
        ]
        
        try:
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(exist_ok=True)
                logger.info(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Directory creation failed: {e}")
            return False
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("🐍 Installing Python dependencies...")
        
        try:
            # Upgrade pip first
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True)
            
            # Install basic requirements
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                logger.info("Installing from requirements.txt...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True)
            else:
                logger.warning("⚠️ requirements.txt not found, installing core dependencies...")
                core_deps = [
                    "torch>=2.0.0",
                    "torchaudio>=2.0.0", 
                    "transformers>=4.30.0",
                    "numpy>=1.24.0",
                    "pyaudio>=0.2.11",
                    "pydantic>=2.0.0",
                    "fastapi>=0.100.0",
                    "uvicorn>=0.23.0"
                ]
                
                for dep in core_deps:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", dep
                    ], check=True)
            
            logger.info("✅ Python dependencies installed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Python dependency installation failed: {e}")
            return False
    
    def setup_configuration(self) -> bool:
        """Setup configuration files"""
        logger.info("⚙️ Setting up configuration...")
        
        try:
            # Copy example env file
            env_example = self.project_root / ".env.example"
            env_file = self.project_root / ".env"
            
            if env_example.exists() and not env_file.exists():
                import shutil
                shutil.copy(env_example, env_file)
                logger.info("✅ Created .env file from example")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration setup failed: {e}")
            return False
    
    def test_installation(self) -> bool:
        """Test the installation"""
        logger.info("🧪 Testing installation...")
        
        try:
            # Try importing main modules
            sys.path.insert(0, str(self.project_root))
            
            from src.config import settings
            logger.info("✅ Configuration module imported")
            
            from src.voice_engine import VoiceManager
            logger.info("✅ Voice engine module imported")
            
            from src.characters import PersonalityManager
            logger.info("✅ Character system module imported")
            
            # Test basic functionality
            personality_manager = PersonalityManager()
            personalities = personality_manager.get_available_personalities()
            logger.info(f"✅ Found {len(personalities)} personalities")
            
            logger.info("✅ Installation test passed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Installation test failed: {e}")
            return False
    
    def run_installation(self) -> bool:
        """Run complete installation process"""
        logger.info("🚀 Starting AI Voice Streaming Host installation...")
        
        steps = [
            ("Checking requirements", self.check_requirements),
            ("Installing system dependencies", self.install_system_dependencies),
            ("Creating directories", self.create_directories),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Setting up configuration", self.setup_configuration),
            ("Testing installation", self.test_installation)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            if not step_func():
                logger.error(f"❌ Installation failed at: {step_name}")
                return False
        
        logger.info("🎉 Installation completed successfully!")
        logger.info("🎤 You can now run the demo with: python demo.py")
        logger.info("🎮 Or start the full application with: python main.py")
        
        return True


def main():
    """Main installation function"""
    installer = Installer()
    
    try:
        success = installer.run_installation()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("🛑 Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Installation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

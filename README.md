# AI Voice Streaming Host / AI语音直播主播

🎤 **A sophisticated AI-powered voice streaming system for live platforms like 抖音 (Douyin)**

一个专为抖音等直播平台设计的先进AI语音主播系统，支持多语言、多个性、ASMR模式的虚拟主播。

## ✨ Features / 功能特点

### 🎯 Core Features / 核心功能
- **Multi-language Support** / **多语言支持**: Chinese (中文) and English with auto-detection
- **Real-time Voice Generation** / **实时语音生成**: Low-latency streaming optimized for live platforms
- **Multiple Personalities** / **多种个性**: Cute girl, ASMR, energetic, shy, and more character types
- **ASMR Capabilities** / **ASMR功能**: Specialized modes for relaxing and sleep-inducing content
- **Voice Cloning** / **声音克隆**: Clone voices from audio samples for custom characters
- **Roleplay Scenarios** / **角色扮演**: Pre-defined scenarios like maid cafe, girlfriend, little sister

### 🎵 Voice Engines / 语音引擎
- **XTTS-v2**: State-of-the-art multilingual TTS with voice cloning (Primary)
- **ChatTTS**: Optimized for Chinese/English conversational speech (Fallback)
- **RealtimeTTS**: Real-time streaming wrapper for minimal latency

### 👤 Character System / 角色系统
- **Personality Profiles** / **个性档案**: Different speaking styles and emotional tendencies
- **Voice Modulation** / **声音调制**: Pitch, speed, and emotion adjustments
- **Dynamic Responses** / **动态回应**: Context-aware responses with catchphrases
- **Character Switching** / **角色切换**: Real-time personality changes during streams

### 🎭 ASMR Modes / ASMR模式
- **Gentle Whisper** / **温柔耳语**: Soft whispers for relaxation
- **Personal Attention** / **个人关怀**: Caring and intimate interactions
- **Rain & Nature** / **雨声自然**: Nature sounds with gentle voice
- **Tapping & Sounds** / **敲击音效**: Various trigger sounds
- **Roleplay ASMR** / **角色扮演ASMR**: Immersive scenarios

## 🚀 Quick Start / 快速开始

### Prerequisites / 前置要求

```bash
# Python 3.8+ required
python --version

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install portaudio19-dev python3-dev

# For macOS
brew install portaudio

# For Windows
# Download and install Microsoft Visual C++ Build Tools
```

### Installation / 安装

#### Option 1: Automated Installation / 自动安装 (Recommended)

```bash
# Clone the repository / 克隆仓库
git clone https://github.com/your-username/ai-voice-streaming-host.git
cd ai-voice-streaming-host

# Run automated installation / 运行自动安装
python install.py
```

#### Option 2: Manual Installation / 手动安装

1. **Clone the repository / 克隆仓库**
```bash
git clone https://github.com/your-username/ai-voice-streaming-host.git
cd ai-voice-streaming-host
```

2. **Install system dependencies / 安装系统依赖**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install portaudio19-dev python3-dev build-essential ffmpeg

# macOS (with Homebrew)
brew install portaudio ffmpeg

# Windows
# Install Microsoft Visual C++ Build Tools
# Install FFmpeg and add to PATH
```

3. **Install Python dependencies / 安装Python依赖**
```bash
pip install -r requirements.txt
```

4. **Setup configuration / 设置配置**
```bash
cp .env.example .env
# Edit .env file with your settings
```

5. **Test installation / 测试安装**
```bash
python demo.py
```

## 🎮 Usage / 使用方法

### Demo Mode / 演示模式
```bash
python main.py --mode demo --personality cute_girl
```
Runs a demonstration with different personalities and ASMR modes.

### Interactive Mode / 交互模式
```bash
python main.py --mode interactive
```

**Available Commands / 可用命令:**
- `!personality <name>` - Switch personality / 切换个性
- `!asmr <mode>` - Switch ASMR mode / 切换ASMR模式
- `!stats` - Show statistics / 显示统计
- `!help` - Show help / 显示帮助

**Example Interaction / 交互示例:**
```
📝 Enter message: 大家好！欢迎来到我的直播间！
📝 Enter message: !personality asmr_girl
📝 Enter message: !asmr gentle_whisper
📝 Enter message: 轻轻地放松一下...
```

## 🎯 Character Personalities / 角色个性

### Available Personalities / 可用个性

| Name | Display Name | Description |
|------|-------------|-------------|
| `cute_girl` | 可爱小萌妹 | Sweet and adorable girl with cheerful voice |
| `asmr_girl` | 温柔ASMR姐姐 | Gentle ASMR voice for relaxation |
| `energetic_girl` | 活力满满小姐姐 | High-energy and enthusiastic personality |
| `shy_girl` | 害羞小妹妹 | Shy and introverted character |

### ASMR Modes / ASMR模式

| Mode | Name | Description |
|------|------|-------------|
| `gentle_whisper` | 温柔耳语 | Soft whispers for sleep |
| `personal_attention` | 个人关怀 | Caring personal attention |
| `rain_nature` | 雨声自然 | Rain sounds with gentle voice |
| `tapping_sounds` | 敲击音效 | Tapping and trigger sounds |

## 🔧 Configuration / 配置

### Environment Variables / 环境变量
Create a `.env` file:
```env
AIVOICE_USE_GPU=true
AIVOICE_SAMPLE_RATE=22050
AIVOICE_MAX_LATENCY_MS=200
AIVOICE_STREAMING_PLATFORM=douyin
AIVOICE_LOG_LEVEL=INFO
```

### Voice Samples / 语音样本
Place voice samples in the `voices/` directory:
```
voices/
├── cute_girl_sample.wav
├── asmr_girl_sample.wav
└── custom_voice.wav
```

## 🎬 Integration with 抖音 (Douyin)

### OBS Studio Setup / OBS设置
1. Install OBS Studio
2. Add "Audio Input Capture" source
3. Select the virtual audio device created by the application
4. Configure streaming settings for 抖音

### Virtual Audio Device / 虚拟音频设备
The application creates a virtual audio output that can be captured by streaming software.

## 📊 Performance / 性能

### System Requirements / 系统要求
- **CPU**: Intel i5 / AMD Ryzen 5 or better
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Storage**: 5GB for models and cache

### Latency Optimization / 延迟优化
- Target latency: <200ms for real-time streaming
- Automatic buffer size adjustment
- GPU acceleration when available
- Optimized audio processing pipeline

## 🛠️ Development / 开发

### Project Structure / 项目结构
```
ai-voice-streaming-host/
├── src/
│   ├── voice_engine/          # TTS engines
│   ├── characters/            # Personality system
│   ├── streaming/             # Audio streaming
│   ├── language/              # Text processing
│   └── config/                # Configuration
├── models/                    # Model storage
├── voices/                    # Voice samples
├── logs/                      # Application logs
└── main.py                    # Main application
```

### Adding Custom Personalities / 添加自定义个性
```python
from src.characters import PersonalityManager, PersonalityTraits

personality = PersonalityTraits(
    name="custom_character",
    description="My custom character",
    voice_pitch=1.1,
    voice_speed=1.0,
    emotion_tendency="happy",
    catchphrases=["Hello!", "Nice to meet you!"]
)

personality_manager.add_custom_personality(personality)
```

### Voice Cloning / 声音克隆
```python
from src.characters import VoiceProfileManager

voice_manager = VoiceProfileManager()
voice_manager.clone_voice_from_sample(
    character_name="base_character",
    sample_path="path/to/voice_sample.wav",
    new_character_name="cloned_character"
)
```

## 🤝 Contributing / 贡献

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments / 致谢

- **Coqui TTS** for XTTS-v2 model
- **ChatTTS** for Chinese TTS optimization
- **RealtimeTTS** for streaming capabilities
- **抖音 (Douyin)** platform inspiration

## 📞 Support / 支持

- 📧 Email: support@example.com
- 💬 Discord: [Join our server](https://discord.gg/example)
- 📖 Documentation: [Full docs](https://docs.example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/ai-voice-streaming-host/issues)

---

**Made with ❤️ for the streaming community / 为直播社区用心打造**

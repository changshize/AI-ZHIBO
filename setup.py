"""
Setup script for AI Voice Streaming Host
"""
from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-voice-streaming-host",
    version="1.0.0",
    author="AI Voice Team",
    author_email="contact@aivoice.com",
    description="AI-powered voice streaming system for live platforms like 抖音 (Douyin)",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ai-voice-streaming-host",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Content Creators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
        "gpu": [
            "nvidia-ml-py3>=7.352.0",
        ],
        "full": [
            "ChatTTS>=0.1.0",
            "opencc-python-reimplemented>=0.1.7",
            "jieba>=0.42.1",
            "langdetect>=1.0.9",
            "emoji>=2.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ai-voice-host=main:main",
            "ai-voice-demo=demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["config/*.yaml", "config/*.json"],
    },
    keywords=[
        "ai", "voice", "tts", "streaming", "douyin", "live", "virtual", "host",
        "chinese", "english", "asmr", "personality", "character", "roleplay"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/ai-voice-streaming-host/issues",
        "Source": "https://github.com/your-username/ai-voice-streaming-host",
        "Documentation": "https://docs.example.com",
    },
)

"""
Audio Streamer - Handles real-time audio streaming for live platforms
"""
import asyncio
import threading
import queue
import time
import numpy as np
from typing import Optional, Callable, Generator, Any
import logging

try:
    import pyaudio
except ImportError:
    pyaudio = None
    print("Warning: PyAudio not installed. Install with: pip install pyaudio")

try:
    import soundfile as sf
except ImportError:
    sf = None
    print("Warning: SoundFile not installed. Install with: pip install soundfile")

from ..config import settings

logger = logging.getLogger(__name__)


class AudioStreamer:
    """Real-time audio streaming manager"""
    
    def __init__(self):
        self.sample_rate = settings.sample_rate
        self.channels = settings.channels
        self.chunk_size = settings.chunk_size
        self.format = pyaudio.paInt16 if pyaudio else None
        
        self.audio_queue = queue.Queue(maxsize=100)
        self.output_stream = None
        self.input_stream = None
        self.pyaudio_instance = None
        
        self.is_streaming = False
        self.is_recording = False
        self.stream_thread = None
        self.callback_function = None
        
        # Performance monitoring
        self.latency_ms = 0
        self.buffer_underruns = 0
        self.last_audio_time = 0
    
    def initialize(self) -> bool:
        """Initialize audio streaming system"""
        try:
            if pyaudio is None:
                logger.error("PyAudio not available")
                return False
            
            self.pyaudio_instance = pyaudio.PyAudio()
            logger.info("Audio streamer initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize audio streamer: {e}")
            return False
    
    def start_output_stream(self, callback: Optional[Callable] = None) -> bool:
        """Start audio output stream"""
        try:
            if not self.pyaudio_instance:
                if not self.initialize():
                    return False
            
            self.callback_function = callback
            
            # Create output stream
            self.output_stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._output_callback if not callback else None
            )
            
            self.is_streaming = True
            
            # Start streaming thread if no callback provided
            if not callback:
                self.stream_thread = threading.Thread(target=self._stream_worker)
                self.stream_thread.daemon = True
                self.stream_thread.start()
            
            logger.info("Audio output stream started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start output stream: {e}")
            return False
    
    def start_input_stream(self) -> bool:
        """Start audio input stream (for monitoring/feedback)"""
        try:
            if not self.pyaudio_instance:
                if not self.initialize():
                    return False
            
            self.input_stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._input_callback
            )
            
            self.is_recording = True
            logger.info("Audio input stream started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start input stream: {e}")
            return False
    
    def _output_callback(self, in_data, frame_count, time_info, status):
        """PyAudio output callback"""
        try:
            # Get audio data from queue
            if not self.audio_queue.empty():
                audio_data = self.audio_queue.get_nowait()
                
                # Convert to bytes if needed
                if isinstance(audio_data, np.ndarray):
                    audio_data = (audio_data * 32767).astype(np.int16).tobytes()
                
                # Pad or truncate to frame_count
                required_bytes = frame_count * self.channels * 2  # 2 bytes per int16
                if len(audio_data) < required_bytes:
                    audio_data += b'\x00' * (required_bytes - len(audio_data))
                elif len(audio_data) > required_bytes:
                    audio_data = audio_data[:required_bytes]
                
                self.last_audio_time = time.time()
                return (audio_data, pyaudio.paContinue)
            else:
                # No audio available - output silence
                self.buffer_underruns += 1
                silence = b'\x00' * (frame_count * self.channels * 2)
                return (silence, pyaudio.paContinue)
                
        except Exception as e:
            logger.error(f"Output callback error: {e}")
            silence = b'\x00' * (frame_count * self.channels * 2)
            return (silence, pyaudio.paContinue)
    
    def _input_callback(self, in_data, frame_count, time_info, status):
        """PyAudio input callback"""
        try:
            # Process input audio if needed (for monitoring/feedback)
            if self.callback_function:
                self.callback_function(in_data)
            
            return (in_data, pyaudio.paContinue)
            
        except Exception as e:
            logger.error(f"Input callback error: {e}")
            return (in_data, pyaudio.paContinue)
    
    def _stream_worker(self):
        """Background streaming worker thread"""
        while self.is_streaming:
            try:
                # Monitor queue size and latency
                queue_size = self.audio_queue.qsize()
                current_time = time.time()
                
                if self.last_audio_time > 0:
                    self.latency_ms = (current_time - self.last_audio_time) * 1000
                
                # Log performance metrics periodically
                if int(current_time) % 10 == 0:  # Every 10 seconds
                    logger.debug(f"Queue size: {queue_size}, Latency: {self.latency_ms:.1f}ms, "
                               f"Buffer underruns: {self.buffer_underruns}")
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Stream worker error: {e}")
                time.sleep(1)
    
    def queue_audio(self, audio_data: np.ndarray) -> bool:
        """Queue audio data for streaming"""
        try:
            if not self.is_streaming:
                return False
            
            # Convert numpy array to appropriate format
            if isinstance(audio_data, np.ndarray):
                # Ensure correct shape and type
                if audio_data.ndim == 1:
                    audio_data = audio_data.reshape(-1, 1) if self.channels == 1 else np.column_stack([audio_data, audio_data])
                
                # Normalize and convert to int16
                audio_data = np.clip(audio_data, -1.0, 1.0)
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                # Add to queue
                if not self.audio_queue.full():
                    self.audio_queue.put(audio_int16)
                    return True
                else:
                    logger.warning("Audio queue full, dropping frame")
                    return False
            else:
                logger.error("Invalid audio data type")
                return False
                
        except Exception as e:
            logger.error(f"Failed to queue audio: {e}")
            return False
    
    def stream_audio_generator(self, audio_generator: Generator[np.ndarray, None, None]):
        """Stream audio from generator"""
        try:
            for audio_chunk in audio_generator:
                if not self.is_streaming:
                    break
                
                if audio_chunk is not None:
                    self.queue_audio(audio_chunk)
                
                # Small delay to prevent overwhelming the queue
                time.sleep(0.001)
                
        except Exception as e:
            logger.error(f"Audio generator streaming failed: {e}")
    
    def save_stream_to_file(self, filename: str, duration_seconds: float = 10.0) -> bool:
        """Save current stream to audio file"""
        try:
            if sf is None:
                logger.error("SoundFile not available for saving")
                return False
            
            # Collect audio data for specified duration
            audio_data = []
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                if not self.audio_queue.empty():
                    chunk = self.audio_queue.get()
                    if isinstance(chunk, np.ndarray):
                        audio_data.append(chunk)
                time.sleep(0.01)
            
            if audio_data:
                # Concatenate and save
                full_audio = np.concatenate(audio_data, axis=0)
                sf.write(filename, full_audio, self.sample_rate)
                logger.info(f"Stream saved to {filename}")
                return True
            else:
                logger.warning("No audio data to save")
                return False
                
        except Exception as e:
            logger.error(f"Failed to save stream: {e}")
            return False
    
    def get_stream_stats(self) -> dict:
        """Get streaming statistics"""
        return {
            "is_streaming": self.is_streaming,
            "is_recording": self.is_recording,
            "queue_size": self.audio_queue.qsize(),
            "latency_ms": self.latency_ms,
            "buffer_underruns": self.buffer_underruns,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_size": self.chunk_size
        }
    
    def adjust_latency(self, target_latency_ms: float = 200.0):
        """Adjust streaming parameters to achieve target latency"""
        try:
            current_latency = self.latency_ms
            
            if current_latency > target_latency_ms * 1.5:
                # Latency too high - reduce buffer size
                new_chunk_size = max(256, self.chunk_size // 2)
                logger.info(f"Reducing chunk size from {self.chunk_size} to {new_chunk_size}")
                self.chunk_size = new_chunk_size
            elif current_latency < target_latency_ms * 0.5:
                # Latency too low - increase buffer size for stability
                new_chunk_size = min(4096, self.chunk_size * 2)
                logger.info(f"Increasing chunk size from {self.chunk_size} to {new_chunk_size}")
                self.chunk_size = new_chunk_size
                
        except Exception as e:
            logger.error(f"Failed to adjust latency: {e}")
    
    def stop_streaming(self):
        """Stop audio streaming"""
        try:
            self.is_streaming = False
            self.is_recording = False
            
            if self.output_stream:
                self.output_stream.stop_stream()
                self.output_stream.close()
                self.output_stream = None
            
            if self.input_stream:
                self.input_stream.stop_stream()
                self.input_stream.close()
                self.input_stream = None
            
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=2.0)
            
            logger.info("Audio streaming stopped")
            
        except Exception as e:
            logger.error(f"Error stopping streaming: {e}")
    
    def cleanup(self):
        """Cleanup audio resources"""
        self.stop_streaming()
        
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except Exception as e:
                logger.error(f"Error terminating PyAudio: {e}")
            self.pyaudio_instance = None
        
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        logger.info("Audio streamer cleaned up")

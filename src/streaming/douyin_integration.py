"""
Douyin Integration - Specialized integration for 抖音 (Douyin) live streaming
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
import threading
import time

try:
    import websockets
except ImportError:
    websockets = None
    print("Warning: websockets not installed. Install with: pip install websockets")

from ..config import settings

logger = logging.getLogger(__name__)


class DouyinIntegration:
    """Integration with 抖音 (Douyin) live streaming platform"""
    
    def __init__(self):
        self.is_connected = False
        self.websocket = None
        self.room_id = None
        self.streamer_info = {}
        
        # Callbacks
        self.on_comment_callback = None
        self.on_gift_callback = None
        self.on_follow_callback = None
        self.on_like_callback = None
        
        # Statistics
        self.stats = {
            "comments_received": 0,
            "gifts_received": 0,
            "new_followers": 0,
            "likes_received": 0,
            "viewers_count": 0
        }
        
        # Message queue for processing
        self.message_queue = asyncio.Queue()
        self.is_processing = False
    
    async def connect(self, room_id: str, auth_token: Optional[str] = None) -> bool:
        """Connect to Douyin live stream"""
        try:
            if websockets is None:
                logger.error("WebSockets library not available")
                return False
            
            self.room_id = room_id
            
            # Douyin WebSocket URL (this is a placeholder - actual implementation would need real API)
            ws_url = f"wss://webcast.douyin.com/webcast/im/push/v2/?room_id={room_id}"
            
            if auth_token:
                ws_url += f"&token={auth_token}"
            
            logger.info(f"Connecting to Douyin room: {room_id}")
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Origin": "https://live.douyin.com"
                }
            )
            
            self.is_connected = True
            logger.info("✅ Connected to Douyin live stream")
            
            # Start message processing
            asyncio.create_task(self._message_listener())
            asyncio.create_task(self._message_processor())
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Douyin: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Douyin live stream"""
        try:
            self.is_connected = False
            self.is_processing = False
            
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            logger.info("Disconnected from Douyin live stream")
            
        except Exception as e:
            logger.error(f"Error disconnecting from Douyin: {e}")
    
    async def _message_listener(self):
        """Listen for messages from Douyin WebSocket"""
        try:
            while self.is_connected and self.websocket:
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=30.0
                    )
                    
                    # Parse message and add to queue
                    parsed_message = self._parse_douyin_message(message)
                    if parsed_message:
                        await self.message_queue.put(parsed_message)
                        
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await self._send_ping()
                except Exception as e:
                    logger.error(f"Message listener error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Message listener failed: {e}")
        finally:
            self.is_connected = False
    
    async def _message_processor(self):
        """Process messages from the queue"""
        self.is_processing = True
        
        try:
            while self.is_processing:
                try:
                    # Get message from queue
                    message = await asyncio.wait_for(
                        self.message_queue.get(),
                        timeout=1.0
                    )
                    
                    # Process based on message type
                    await self._handle_message(message)
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Message processing error: {e}")
                    
        except Exception as e:
            logger.error(f"Message processor failed: {e}")
        finally:
            self.is_processing = False
    
    def _parse_douyin_message(self, raw_message: str) -> Optional[Dict[str, Any]]:
        """Parse raw Douyin message"""
        try:
            # This is a simplified parser - actual implementation would need
            # to handle Douyin's specific message format
            
            if isinstance(raw_message, bytes):
                raw_message = raw_message.decode('utf-8')
            
            # Try to parse as JSON
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                # Handle non-JSON messages
                return {"type": "raw", "content": raw_message}
            
            # Extract message type and content
            message_type = data.get("type", "unknown")
            
            if message_type == "chat":
                return {
                    "type": "comment",
                    "user": data.get("user", {}).get("nickname", "Anonymous"),
                    "content": data.get("content", ""),
                    "timestamp": data.get("timestamp", time.time())
                }
            elif message_type == "gift":
                return {
                    "type": "gift",
                    "user": data.get("user", {}).get("nickname", "Anonymous"),
                    "gift_name": data.get("gift", {}).get("name", "Unknown"),
                    "gift_count": data.get("gift", {}).get("count", 1),
                    "timestamp": data.get("timestamp", time.time())
                }
            elif message_type == "follow":
                return {
                    "type": "follow",
                    "user": data.get("user", {}).get("nickname", "Anonymous"),
                    "timestamp": data.get("timestamp", time.time())
                }
            elif message_type == "like":
                return {
                    "type": "like",
                    "user": data.get("user", {}).get("nickname", "Anonymous"),
                    "count": data.get("count", 1),
                    "timestamp": data.get("timestamp", time.time())
                }
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to parse Douyin message: {e}")
            return None
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Handle parsed message"""
        try:
            message_type = message.get("type")
            
            if message_type == "comment":
                self.stats["comments_received"] += 1
                if self.on_comment_callback:
                    await self._safe_callback(
                        self.on_comment_callback,
                        message["user"],
                        message["content"]
                    )
            
            elif message_type == "gift":
                self.stats["gifts_received"] += 1
                if self.on_gift_callback:
                    await self._safe_callback(
                        self.on_gift_callback,
                        message["user"],
                        message["gift_name"],
                        message["gift_count"]
                    )
            
            elif message_type == "follow":
                self.stats["new_followers"] += 1
                if self.on_follow_callback:
                    await self._safe_callback(
                        self.on_follow_callback,
                        message["user"]
                    )
            
            elif message_type == "like":
                self.stats["likes_received"] += message.get("count", 1)
                if self.on_like_callback:
                    await self._safe_callback(
                        self.on_like_callback,
                        message["user"],
                        message.get("count", 1)
                    )
            
        except Exception as e:
            logger.error(f"Message handling error: {e}")
    
    async def _safe_callback(self, callback: Callable, *args):
        """Safely execute callback"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Callback execution error: {e}")
    
    async def _send_ping(self):
        """Send ping to keep connection alive"""
        try:
            if self.websocket:
                ping_message = json.dumps({"type": "ping", "timestamp": time.time()})
                await self.websocket.send(ping_message)
        except Exception as e:
            logger.error(f"Failed to send ping: {e}")
    
    def set_comment_callback(self, callback: Callable[[str, str], None]):
        """Set callback for comments"""
        self.on_comment_callback = callback
    
    def set_gift_callback(self, callback: Callable[[str, str, int], None]):
        """Set callback for gifts"""
        self.on_gift_callback = callback
    
    def set_follow_callback(self, callback: Callable[[str], None]):
        """Set callback for new followers"""
        self.on_follow_callback = callback
    
    def set_like_callback(self, callback: Callable[[str, int], None]):
        """Set callback for likes"""
        self.on_like_callback = callback
    
    def get_stats(self) -> Dict[str, Any]:
        """Get streaming statistics"""
        return {
            **self.stats,
            "is_connected": self.is_connected,
            "room_id": self.room_id,
            "connection_time": time.time() if self.is_connected else None
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "comments_received": 0,
            "gifts_received": 0,
            "new_followers": 0,
            "likes_received": 0,
            "viewers_count": 0
        }
    
    async def send_message(self, message: str) -> bool:
        """Send message to chat (if supported)"""
        try:
            if not self.is_connected or not self.websocket:
                return False
            
            message_data = {
                "type": "chat",
                "content": message,
                "timestamp": time.time()
            }
            
            await self.websocket.send(json.dumps(message_data))
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def get_room_info(self) -> Dict[str, Any]:
        """Get room information"""
        return {
            "room_id": self.room_id,
            "is_connected": self.is_connected,
            "streamer_info": self.streamer_info,
            "platform": "douyin"
        }
    
    async def update_stream_title(self, title: str) -> bool:
        """Update stream title (if API supports it)"""
        try:
            # This would require Douyin API integration
            logger.info(f"Stream title update requested: {title}")
            # Placeholder implementation
            return True
        except Exception as e:
            logger.error(f"Failed to update stream title: {e}")
            return False
    
    async def get_viewer_count(self) -> int:
        """Get current viewer count"""
        try:
            # This would require API call to get viewer count
            # Placeholder implementation
            return self.stats.get("viewers_count", 0)
        except Exception as e:
            logger.error(f"Failed to get viewer count: {e}")
            return 0


# Example usage and integration helper
class DouyinStreamingBot:
    """High-level bot for Douyin streaming integration"""
    
    def __init__(self, voice_callback: Optional[Callable] = None):
        self.douyin = DouyinIntegration()
        self.voice_callback = voice_callback
        self.auto_responses = True
        
        # Set up callbacks
        self.douyin.set_comment_callback(self._handle_comment)
        self.douyin.set_gift_callback(self._handle_gift)
        self.douyin.set_follow_callback(self._handle_follow)
    
    async def start(self, room_id: str, auth_token: Optional[str] = None):
        """Start the streaming bot"""
        success = await self.douyin.connect(room_id, auth_token)
        if success:
            logger.info("🤖 Douyin streaming bot started")
        return success
    
    async def stop(self):
        """Stop the streaming bot"""
        await self.douyin.disconnect()
        logger.info("🤖 Douyin streaming bot stopped")
    
    async def _handle_comment(self, user: str, content: str):
        """Handle incoming comments"""
        logger.info(f"💬 {user}: {content}")
        
        if self.auto_responses and self.voice_callback:
            # Generate response based on comment
            response = self._generate_response(user, content)
            if response:
                await self.voice_callback(response)
    
    async def _handle_gift(self, user: str, gift_name: str, count: int):
        """Handle gift events"""
        logger.info(f"🎁 {user} sent {count}x {gift_name}")
        
        if self.auto_responses and self.voice_callback:
            response = f"谢谢 {user} 的 {gift_name}！非常感谢！"
            await self.voice_callback(response)
    
    async def _handle_follow(self, user: str):
        """Handle new followers"""
        logger.info(f"👥 {user} followed the stream")
        
        if self.auto_responses and self.voice_callback:
            response = f"欢迎 {user} 关注！谢谢支持！"
            await self.voice_callback(response)
    
    def _generate_response(self, user: str, content: str) -> Optional[str]:
        """Generate appropriate response to comment"""
        content_lower = content.lower()
        
        # Simple response patterns
        if any(word in content_lower for word in ["你好", "hello", "hi"]):
            return f"你好 {user}！欢迎来到直播间！"
        elif any(word in content_lower for word in ["漂亮", "可爱", "beautiful", "cute"]):
            return f"谢谢 {user} 的夸奖！你也很棒哦！"
        elif any(word in content_lower for word in ["唱歌", "sing", "song"]):
            return f"{user} 想听歌吗？我来为大家唱一首！"
        elif any(word in content_lower for word in ["晚安", "goodnight", "睡觉"]):
            return f"晚安 {user}！做个好梦！"
        
        # Default response for engagement
        if len(content) > 5:  # Only respond to substantial comments
            return f"谢谢 {user} 的留言！"
        
        return None

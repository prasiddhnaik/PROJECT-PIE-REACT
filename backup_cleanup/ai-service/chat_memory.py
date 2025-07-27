"""
Chat memory management for AI conversations.
"""

import json
import redis
import asyncio
import time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ChatMemoryManager:
    """Manages conversation history and context."""
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        max_history: int = 20,
        ttl: int = 7200  # 2 hours
    ):
        self.redis_url = redis_url or "redis://localhost:6379"
        self.max_history = max_history
        self.ttl = ttl
        self.redis_client = None
        self.memory_store = {}  # Fallback in-memory store
        
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Chat memory Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed for chat memory, using in-memory store: {e}")
            self.redis_client = None
    
    def _get_conversation_key(self, session_id: str) -> str:
        """Generate Redis key for conversation."""
        return f"chat:conversation:{session_id}"
    
    def _get_metadata_key(self, session_id: str) -> str:
        """Generate Redis key for conversation metadata."""
        return f"chat:metadata:{session_id}"
    
    async def get_conversation(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history."""
        conversation_key = self._get_conversation_key(session_id)
        
        if self.redis_client:
            try:
                # Get conversation from Redis
                conversation_data = self.redis_client.get(conversation_key)
                if conversation_data:
                    conversation = json.loads(conversation_data)
                    # Update access time
                    await self._update_metadata(session_id)
                    return conversation
            except Exception as e:
                logger.error(f"Error getting conversation from Redis: {e}")
        
        # Fallback to memory store
        return self.memory_store.get(conversation_key, [])
    
    async def save_conversation(self, session_id: str, messages: List[Dict[str, str]]) -> bool:
        """Save conversation history."""
        conversation_key = self._get_conversation_key(session_id)
        
        # Trim conversation to max history
        if len(messages) > self.max_history:
            # Keep system messages and recent messages
            system_messages = [msg for msg in messages if msg.get("role") == "system"]
            recent_messages = messages[-(self.max_history - len(system_messages)):]
            messages = system_messages + recent_messages
        
        if self.redis_client:
            try:
                # Save to Redis with TTL
                conversation_data = json.dumps(messages)
                pipe = self.redis_client.pipeline()
                pipe.setex(conversation_key, self.ttl, conversation_data)
                pipe.execute()
                
                # Update metadata
                await self._update_metadata(session_id, len(messages))
                return True
            except Exception as e:
                logger.error(f"Error saving conversation to Redis: {e}")
        
        # Fallback to memory store
        self.memory_store[conversation_key] = messages
        # Simple TTL simulation
        asyncio.create_task(self._expire_memory_conversation(conversation_key))
        return True
    
    async def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history."""
        conversation_key = self._get_conversation_key(session_id)
        metadata_key = self._get_metadata_key(session_id)
        
        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.delete(conversation_key)
                pipe.delete(metadata_key)
                pipe.execute()
                return True
            except Exception as e:
                logger.error(f"Error clearing conversation from Redis: {e}")
        
        # Clear from memory store
        self.memory_store.pop(conversation_key, None)
        return True
    
    async def get_conversation_metadata(self, session_id: str) -> Dict[str, Any]:
        """Get conversation metadata."""
        metadata_key = self._get_metadata_key(session_id)
        
        if self.redis_client:
            try:
                metadata_data = self.redis_client.get(metadata_key)
                if metadata_data:
                    return json.loads(metadata_data)
            except Exception as e:
                logger.error(f"Error getting metadata from Redis: {e}")
        
        # Default metadata
        return {
            "created_at": time.time(),
            "last_accessed": time.time(),
            "message_count": 0,
            "session_id": session_id
        }
    
    async def _update_metadata(self, session_id: str, message_count: Optional[int] = None):
        """Update conversation metadata."""
        metadata_key = self._get_metadata_key(session_id)
        current_time = time.time()
        
        # Get existing metadata
        metadata = await self.get_conversation_metadata(session_id)
        
        # Update metadata
        metadata.update({
            "last_accessed": current_time,
            "session_id": session_id
        })
        
        if message_count is not None:
            metadata["message_count"] = message_count
        
        if "created_at" not in metadata:
            metadata["created_at"] = current_time
        
        if self.redis_client:
            try:
                metadata_data = json.dumps(metadata)
                self.redis_client.setex(metadata_key, self.ttl, metadata_data)
            except Exception as e:
                logger.error(f"Error updating metadata in Redis: {e}")
    
    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List active conversation sessions."""
        active_sessions = []
        
        if self.redis_client:
            try:
                # Get all conversation keys
                pattern = "chat:conversation:*"
                keys = self.redis_client.keys(pattern)
                
                for key in keys:
                    session_id = key.replace("chat:conversation:", "")
                    metadata = await self.get_conversation_metadata(session_id)
                    
                    # Check if session is still active (not expired)
                    if time.time() - metadata.get("last_accessed", 0) < self.ttl:
                        active_sessions.append(metadata)
                
            except Exception as e:
                logger.error(f"Error listing sessions from Redis: {e}")
        
        # Add memory store sessions
        for key in self.memory_store.keys():
            if key.startswith("chat:conversation:"):
                session_id = key.replace("chat:conversation:", "")
                metadata = await self.get_conversation_metadata(session_id)
                active_sessions.append(metadata)
        
        return active_sessions
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired conversation sessions."""
        cleaned_count = 0
        
        if self.redis_client:
            try:
                # Redis handles TTL automatically, but we can clean up metadata
                pattern = "chat:metadata:*"
                keys = self.redis_client.keys(pattern)
                
                for key in keys:
                    try:
                        metadata_data = self.redis_client.get(key)
                        if metadata_data:
                            metadata = json.loads(metadata_data)
                            if time.time() - metadata.get("last_accessed", 0) > self.ttl:
                                session_id = key.replace("chat:metadata:", "")
                                await self.clear_conversation(session_id)
                                cleaned_count += 1
                    except:
                        continue
                        
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
        
        # Clean memory store
        expired_keys = []
        for key in list(self.memory_store.keys()):
            # In a real implementation, you'd track creation time
            # For now, just clean old keys periodically
            if key.startswith("chat:conversation:"):
                expired_keys.append(key)
        
        for key in expired_keys[-cleaned_count:]:  # Clean some old ones
            del self.memory_store[key]
            cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} expired chat sessions")
        return cleaned_count
    
    async def _expire_memory_conversation(self, key: str):
        """Expire conversation from memory store after TTL."""
        await asyncio.sleep(self.ttl)
        self.memory_store.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory manager statistics."""
        stats = {
            "max_history": self.max_history,
            "ttl_seconds": self.ttl,
            "redis_connected": self.redis_client is not None,
            "memory_store_size": len(self.memory_store)
        }
        
        if self.redis_client:
            try:
                # Get Redis memory usage
                info = self.redis_client.info("memory")
                stats["redis_memory_usage"] = info.get("used_memory_human", "N/A")
                
                # Count active sessions
                conversation_keys = self.redis_client.keys("chat:conversation:*")
                stats["active_sessions"] = len(conversation_keys)
            except:
                stats["redis_memory_usage"] = "N/A"
                stats["active_sessions"] = 0
        
        return stats 
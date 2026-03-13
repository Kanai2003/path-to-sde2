"""
Message queue module with lazy initialization for async Redis Streams.

Usage:
    from app.core.message_queue import get_analytics_queue
    
    queue = get_analytics_queue()
    await queue.publish("url:click", {"short_code": "abc123"})
"""

from typing import Optional

from .message_queue import AsyncMessageQueue

# Lazy singleton - initialized after Redis pools are ready
_analytics_queue: Optional[AsyncMessageQueue] = None


def init_queue() -> None:
    """Initialize message queue singleton. Called on app startup after Redis pools init."""
    global _analytics_queue
    
    from app.core.redis_pool import get_queue_redis
    
    _analytics_queue = AsyncMessageQueue(get_queue_redis())


def get_analytics_queue() -> AsyncMessageQueue:
    """Get analytics message queue singleton."""
    if _analytics_queue is None:
        raise RuntimeError("Message queue not initialized. Call init_queue() on startup.")
    return _analytics_queue


__all__ = ["get_analytics_queue", "init_queue", "AsyncMessageQueue"]

"""
High-performance async message queue using Redis Streams.

Redis Streams advantages over Lists:
- Consumer groups: Multiple workers share load automatically
- Message acknowledgment: At-least-once delivery guarantee
- Message persistence: Survives Redis restart
- Backpressure: XREADGROUP blocks efficiently
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.utils.logger import logger


class AsyncMessageQueue:
    """
    Production-grade async message queue using Redis Streams.
    
    Features:
    - Consumer groups for horizontal scaling
    - Automatic message acknowledgment
    - Dead letter queue for failed messages
    - Stream trimming to prevent unbounded growth
    """

    def __init__(self, redis_client: Redis, stream_name: str = "analytics_stream"):
        self.redis = redis_client
        self.stream_name = stream_name
        self.consumer_group = "analytics_workers"
        self.dlq_stream = f"{stream_name}:dlq"
        self._group_created = False

    async def _ensure_consumer_group(self) -> None:
        """Create consumer group if it doesn't exist."""
        if self._group_created:
            return
            
        try:
            await self.redis.xgroup_create(
                self.stream_name,
                self.consumer_group,
                id="0",
                mkstream=True,
            )
            self._group_created = True
        except RedisError as e:
            if "BUSYGROUP" in str(e):
                self._group_created = True
            else:
                logger.error(f"Failed to create consumer group: {e}")

    async def publish(self, event_type: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Publish an event to the stream (non-blocking, fast).

        Args:
            event_type: Event type identifier
            data: Event payload

        Returns:
            Message ID if successful, None otherwise
        """
        message = {
            "event_type": event_type,
            "data": json.dumps(data),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # XADD is O(1) - very fast
            # MAXLEN ~ keeps stream bounded (approximate for performance)
            message_id = await self.redis.xadd(
                self.stream_name,
                message,
                maxlen=1_000_000,
                approximate=True,
            )
            return message_id
        except RedisError as e:
            logger.error(f"Failed to publish event: {e}")
            return None

    async def consume_batch(
        self,
        consumer_name: str,
        count: int = 100,
        block_ms: int = 5000,
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Consume a batch of messages from the stream.

        Args:
            consumer_name: Unique name for this consumer instance
            count: Max messages to fetch
            block_ms: How long to block waiting for messages

        Returns:
            List of (message_id, message_data) tuples
        """
        await self._ensure_consumer_group()

        try:
            result = await self.redis.xreadgroup(
                groupname=self.consumer_group,
                consumername=consumer_name,
                streams={self.stream_name: ">"},
                count=count,
                block=block_ms,
            )

            if not result:
                return []

            messages = []
            for stream_name, stream_messages in result:
                for message_id, message_data in stream_messages:
                    parsed = {
                        "event_type": message_data.get("event_type"),
                        "data": json.loads(message_data.get("data", "{}")),
                        "timestamp": message_data.get("timestamp"),
                    }
                    messages.append((message_id, parsed))

            return messages

        except RedisError as e:
            logger.error(f"Failed to consume messages: {e}")
            return []

    async def acknowledge(self, message_ids: List[str]) -> int:
        """Acknowledge messages as processed."""
        if not message_ids:
            return 0

        try:
            return await self.redis.xack(
                self.stream_name,
                self.consumer_group,
                *message_ids,
            )
        except RedisError as e:
            logger.error(f"Failed to acknowledge messages: {e}")
            return 0

    async def move_to_dlq(self, message_id: str, message: Dict, error: str) -> None:
        """Move failed message to dead letter queue."""
        dlq_message = {
            "original_id": message_id,
            "event_type": message.get("event_type", ""),
            "data": json.dumps(message.get("data", {})),
            "error": error,
            "failed_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            await self.redis.xadd(self.dlq_stream, dlq_message, maxlen=100_000)
            await self.acknowledge([message_id])
        except RedisError as e:
            logger.error(f"Failed to move message to DLQ: {e}")

    async def get_stream_length(self) -> int:
        """Get total messages in stream."""
        try:
            return await self.redis.xlen(self.stream_name)
        except RedisError:
            return 0

    async def claim_stale_messages(
        self,
        consumer_name: str,
        min_idle_ms: int = 60000,
        count: int = 100,
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Claim messages that other consumers failed to process.
        
        Handles worker crashes - messages idle for > min_idle_ms are reassigned.
        """
        try:
            result = await self.redis.xautoclaim(
                self.stream_name,
                self.consumer_group,
                consumer_name,
                min_idle_time=min_idle_ms,
                count=count,
            )

            if not result or not result[1]:
                return []

            messages = []
            for message_id, message_data in result[1]:
                if message_data:  # Skip deleted messages
                    parsed = {
                        "event_type": message_data.get("event_type"),
                        "data": json.loads(message_data.get("data", "{}")),
                        "timestamp": message_data.get("timestamp"),
                    }
                    messages.append((message_id, parsed))

            return messages

        except RedisError as e:
            logger.error(f"Failed to claim stale messages: {e}")
            return []


# Lazy singleton - initialized after Redis pools are ready
_analytics_queue: Optional[AsyncMessageQueue] = None


def init_message_queue() -> None:
    """Initialize message queue singleton. Called on app startup."""
    global _analytics_queue
    from app.core.redis_pool import get_queue_redis
    _analytics_queue = AsyncMessageQueue(get_queue_redis())


def get_analytics_queue() -> AsyncMessageQueue:
    """Get analytics queue singleton."""
    if _analytics_queue is None:
        raise RuntimeError("Message queue not initialized. Call init_message_queue() on startup.")
    return _analytics_queue
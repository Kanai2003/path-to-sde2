import json
from typing import Any, Dict, List, Optional
from datetime import datetime

import redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.utils.logger import logger

class MessageQueue:
    def __init__(self, queue_name: str = "analytics_events"):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            db=getattr(settings, "REDIS_DB_QUEUE", 2),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        self.queue_name = queue_name
        self.dead_letter_queue = f"{queue_name}:dlq"
        
    def publish(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        publish an event to the message queue
        
        Args:
            event_type: Type of events (e.g, "click", "url_created")
            data: Data associated with the event
            
            
        Returns:
            True if the event was published successfully, False otherwise
        """
        
        event = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # LPUSH adds to the left (head) of list
            # Consumer will BRPOP from right (tail) = FIFO
            self.redis_client.lpush(self.queue_name, json.dumps(event))
            return True
        except RedisError as e:
            logger.error(f"Failed to publish event to queue: {e}")
            return False
        
    def consume(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Consume an event from the message queue
        
        Args:
            timeout: Time in seconds to wait for an event before returning None
            
        Returns:
            Message dict or None if timeout
        """
        try:
            # BRPOP returns a tuple (queue_name, message) or None on timeout
            result = self.redis_client.brpop(self.queue_name, timeout=timeout)
            if result:
                _, message = result
                return json.loads(message)
            return None
        except RedisError as e:
            logger.error(f"Failed to consume event from queue: {e}")
            return None
        
    def move_to_dead_letter_queue(self, message: Dict[str, Any], error: str) -> bool:
        """
        Move a failed event to the dead letter queue for later analysis
        """
        message["error"] = error
        message["failed_at"] = datetime.utcnow().isoformat()
        
        try:
            self.redis_client.lpush(self.dead_letter_queue, json.dumps(message))
        except RedisError as e:
            logger.error(f"Failed to move message to dead letter queue: {e}")
    
    
    def get_unique_length(self) -> int:
        """
        Get the number of unique events in the queue (for monitoring purposes)
        """
        try:
            return self.redis_client.llen(self.queue_name)
        except RedisError as e:
            logger.error(f"Failed to get queue length: {e}")
            return 0
    
    def is_available(self) -> bool:
        """
        Check if the Redis server is available
        """
        try:
            self.redis_client.ping()
            return True
        except RedisError as e:
            logger.error(f"Redis server is not available: {e}")
            return False

analytics_queue = MessageQueue(queue_name="analytics_events")
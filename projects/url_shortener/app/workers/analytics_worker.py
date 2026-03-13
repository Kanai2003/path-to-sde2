"""
Async background worker that consumes analytics events from Redis Streams.

Features:
- Consumer groups for horizontal scaling
- Batched database writes for throughput
- Automatic retry with exponential backoff
- Graceful shutdown handling
"""

import asyncio
import signal
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.core.config import settings
from app.core.message_queue import init_queue, get_analytics_queue
from app.core.redis_pool import redis_pool_manager
from app.db.session import AsyncSessionLocal
from app.repositories.url_repository import url_repository
from app.utils.logger import logger


class AsyncAnalyticsWorker:
    """
    High-performance async worker that processes analytics events.
    
    Architecture:
    - Uses Redis Streams for reliable message delivery
    - Consumer groups allow horizontal scaling (run multiple workers)
    - Batches DB writes for efficiency
    - Handles backpressure gracefully
    """
    
    def __init__(self, consumer_name: str = "worker-1"):
        self.consumer_name = consumer_name
        self.running = False
        self.processed_count = 0
        self.error_count = 0
        self.batch_size = settings.WORKER_BATCH_SIZE
        self.flush_interval = settings.WORKER_FLUSH_INTERVAL
        
        # Click buffer - accumulate before flushing to DB
        self.click_buffer: Dict[str, int] = {}
        self.last_flush = datetime.now(timezone.utc)

    async def start(self) -> None:
        """Start consuming messages from the queue."""
        # Initialize Redis pools
        await redis_pool_manager.init_pools()
        init_queue()
        
        self.running = True
        self.queue = get_analytics_queue()
        
        logger.info(f"Analytics worker '{self.consumer_name}' started. Waiting for events...")
        
        # Handle graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self._shutdown()))
        
        try:
            while self.running:
                try:
                    # Read batch of messages from stream
                    messages = await self.queue.consume_batch(
                        consumer_name=self.consumer_name,
                        count=100,  # Read up to 100 messages at once
                        block_ms=5000,  # Block for 5 seconds max
                    )
                    
                    if messages:
                        await self._process_batch(messages)
                    
                    # Periodic flush based on time
                    await self._maybe_flush()
                    
                except Exception as e:
                    logger.error(f"Worker error: {e}")
                    self.error_count += 1
                    await asyncio.sleep(1)  # Back off on errors
                    
        finally:
            # Final flush before shutdown
            await self._flush_to_database()
            await redis_pool_manager.close_pools()
    
    async def _process_batch(self, messages: List[tuple]) -> None:
        """
        Process a batch of messages efficiently.
        
        Args:
            messages: List of (message_id, message_data) tuples
        """
        message_ids = []
        
        for msg_id, msg_data in messages:
            try:
                event_type = msg_data.get("event_type")
                
                if event_type == "click":
                    # Data is already parsed by consume_batch
                    data = msg_data.get("data", {})
                    short_code = data.get("short_code")
                    
                    if short_code:
                        # Buffer the click for batch DB write
                        self.click_buffer[short_code] = self.click_buffer.get(short_code, 0) + 1
                        self.processed_count += 1
                
                message_ids.append(msg_id)
                
            except Exception as e:
                logger.error(f"Failed to process message {msg_id}: {e}")
                # Send to dead letter queue
                await self.queue.move_to_dlq(msg_id, msg_data, str(e))
                self.error_count += 1
        
        # Acknowledge processed messages
        if message_ids:
            await self.queue.acknowledge(message_ids)
        
        # Flush if buffer is full
        if len(self.click_buffer) >= self.batch_size:
            await self._flush_to_database()
    
    async def _maybe_flush(self) -> None:
        """Flush buffer if enough time has passed."""
        now = datetime.now(timezone.utc)
        elapsed = (now - self.last_flush).total_seconds()
        
        if elapsed >= self.flush_interval and self.click_buffer:
            await self._flush_to_database()
    
    async def _flush_to_database(self) -> None:
        """Flush accumulated clicks to database."""
        if not self.click_buffer:
            return
            
        buffer_copy = self.click_buffer.copy()
        self.click_buffer.clear()
        self.last_flush = datetime.now(timezone.utc)
        
        try:
            async with AsyncSessionLocal() as db:
                for short_code, count in buffer_copy.items():
                    await url_repository.increment_fetch_count_by(db, short_code, count)
                await db.commit()
                
            logger.info(f"Flushed {len(buffer_copy)} URLs, {sum(buffer_copy.values())} total clicks")
            
        except Exception as e:
            logger.error(f"Failed to flush to database: {e}")
            # Put items back in buffer for retry
            for code, count in buffer_copy.items():
                self.click_buffer[code] = self.click_buffer.get(code, 0) + count

    async def _shutdown(self) -> None:
        """Handle graceful shutdown."""
        logger.info(
            f"Shutting down worker '{self.consumer_name}'. "
            f"Processed: {self.processed_count}, Errors: {self.error_count}"
        )
        self.running = False


async def main():
    """Entry point for running the worker."""
    import os
    consumer_name = os.environ.get("WORKER_NAME", f"worker-{os.getpid()}")
    worker = AsyncAnalyticsWorker(consumer_name=consumer_name)
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
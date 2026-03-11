"""Background worker that consumes analytics events from the queue."""

import signal
import sys
from typing import Dict, Any

from app.core.message_queue.message_queue import analytics_queue
from app.core.cache.analytics_cache import analytics_cache
from app.utils.logger import logger


class AnalyticsWorker:
    """
    Worker that processes analytics events from the message queue.
    
    This runs as a separate process, decoupled from the web app.
    """
    
    def __init__(self):
        self.running = False
        self.processed_count = 0
        self.error_count = 0
    
    def start(self) -> None:
        """Start consuming messages from the queue."""
        self.running = True
        logger.info("Analytics worker started. Waiting for events...")
        
        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
        
        while self.running:
            try:
                # Block until a message arrives (or timeout)
                message = analytics_queue.consume(timeout=5)
                
                if message:
                    self._process_message(message)
                    
            except Exception as e:
                logger.error(f"Worker error: {e}")
                self.error_count += 1
    
    def _process_message(self, message: Dict[str, Any]) -> None:
        """Process a single analytics event."""
        event_type = message.get("event_type")
        data = message.get("data", {})
        
        try:
            if event_type == "click":
                short_code = data.get("short_code")
                if short_code:
                    # Now increment the counter (this is the actual work)
                    analytics_cache.increment_click_count(short_code)
                    self.processed_count += 1
                    logger.debug(f"Processed click for {short_code}")
            
            # Add more event types as needed
            elif event_type == "url_created":
                # Handle URL creation events
                pass
                
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            analytics_queue.move_to_dlq(message, str(e))
            self.error_count += 1
    
    def _shutdown(self, signum, frame) -> None:
        """Handle graceful shutdown."""
        logger.info(f"Shutting down worker. Processed: {self.processed_count}, Errors: {self.error_count}")
        self.running = False
        sys.exit(0)


def main():
    """Entry point for running the worker."""
    worker = AnalyticsWorker()
    worker.start()


if __name__ == "__main__":
    main()
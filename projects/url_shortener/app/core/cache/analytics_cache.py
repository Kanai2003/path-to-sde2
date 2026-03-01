from redis.exceptions import RedisError
from app.core.cache.base_cache import BaseCache

class AnalyticsCache(BaseCache):
    """Cache implementations for analytics data in URL shortener using Redis."""
    
    def __init__(self):
        super().__init__(key_prefix="URL_ANALYTICS")
        self.CLICK_KEY = self._make_key("click_counts")
        
    def increment_click_count(self, short_code: str) -> None:
        """
        Increment the click count for a given short code.
        
        Args: 
            short_code: The short code for which to increment the click count.
        """
        
        try:
            key = self.CLICK_KEY
            self.redis_client.hincrby(key, short_code, 1)
        except RedisError as e:
            self._handle_redis_error(e, "increment_click_count")
            return None
        
    def get_click_count(self, short_code: str) -> int:
        """
        Get the click count for a given short code.
        
        Args:
            short_code: The short code for which to retrieve the click count.
        """
        try:
            key = self.CLICK_KEY
            count = self.redis_client.hget(key, short_code)
            return int(count) if count else 0
        except RedisError as e:
            self._handle_redis_error(e, "get_click_count")
            return 0
    
    def get_all_clicks(self) -> Dict[str, int]:
        """
        Get all clicks counts for all short codes.
        """
        try:
            key = self.CLICK_KEY
            click_data = self.redis_client.hgetall(key)
            return {short_code: int(count) for short_code, count in click_data.items()}
            
        except RedisError as e:
            self._handle_redis_error(e, "get_all_clicks")
            return {}
    
    def reset_clicks(self, short_codes: List[str]) -> None:
        """
        Reset the click count for a given short code to zero.
        
        Args:
            short_codes: The list of short codes for which to reset the click count.
        """
        try:
            key = self.CLICK_KEY
            if short_codes:
                self.redis_client.hdel(key, *short_codes)
        except RedisError as e:
            self._handle_redis_error(e, "reset_clicks")
        
# Singleton instance of Analytics Cache for use across the application
analytics_cache = AnalyticsCache()
    
      
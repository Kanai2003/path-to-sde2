#!/usr/bin/env python3
"""Test script for analytics integration."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.cache.analytics_cache import analytics_cache
from app.core.cache.url_cache import url_cache


def test_redis_connection():
    """Test Redis connectivity."""
    print("Testing Redis connection...")

    if not analytics_cache.is_available():
        print("❌ Analytics cache Redis not available")
        return False

    if not url_cache.is_available():
        print("❌ URL cache Redis not available")
        return False

    print("✅ Redis connection successful")
    return True


def test_analytics_operations():
    """Test analytics cache operations."""
    print("\nTesting analytics operations...")

    # Test increment
    test_code = "test123"
    analytics_cache.increment_click_count(test_code)
    count = analytics_cache.get_click_count(test_code)

    if count != 1:
        print(f"❌ Expected count 1, got {count}")
        return False

    print(f"✅ Click increment works: {count}")

    # Test get all
    all_clicks = analytics_cache.get_all_clicks()
    if test_code not in all_clicks or all_clicks[test_code] != 1:
        print(f"❌ Get all clicks failed: {all_clicks}")
        return False

    print(f"✅ Get all clicks works: {all_clicks}")

    # Test reset
    analytics_cache.reset_clicks([test_code])
    count_after_reset = analytics_cache.get_click_count(test_code)

    if count_after_reset != 0:
        print(f"❌ Reset failed, count still {count_after_reset}")
        return False

    print("✅ Reset clicks works")
    return True


def test_url_cache_operations():
    """Test URL cache operations."""
    print("\nTesting URL cache operations...")

    test_code = "test456"
    test_url = "https://example.com"

    # Test cache set/get
    url_cache.cache_url(test_code, test_url, ttl=60)
    cached_url = url_cache.get_cached_url(test_code)

    if cached_url != test_url:
        print(f"❌ URL cache failed: expected {test_url}, got {cached_url}")
        return False

    print(f"✅ URL cache works: {cached_url}")

    # Test invalidate
    url_cache.invalidate_cache(test_code)
    cached_url_after = url_cache.get_cached_url(test_code)

    if cached_url_after is not None:
        print(f"❌ Cache invalidation failed: still got {cached_url_after}")
        return False

    print("✅ Cache invalidation works")
    return True


if __name__ == "__main__":
    print("🔍 Testing Analytics Cache Integration")
    print("=" * 40)

    success = True
    success &= test_redis_connection()
    success &= test_analytics_operations()
    success &= test_url_cache_operations()

    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! Analytics integration is working.")
    else:
        print("❌ Some tests failed. Check Redis configuration.")
        sys.exit(1)

#!/usr/bin/env python3
"""
Load testing script for URL Shortener API.
No external dependencies - uses only Python standard library.

Usage:
    python scripts/load_test.py
    python scripts/load_test.py --url http://localhost:8080 --requests 500 --concurrent 50
"""

import argparse
import json
import random
import string
import threading
import time
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class RequestResult:
    """Result of a single request."""
    success: bool
    status_code: int
    response_time: float  # in milliseconds
    error: Optional[str] = None


@dataclass
class TestResults:
    """Aggregated test results."""
    test_name: str
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    total_time: float = 0  # seconds
    response_times: list = field(default_factory=list)
    status_codes: dict = field(default_factory=lambda: defaultdict(int))
    errors: list = field(default_factory=list)

    @property
    def rps(self) -> float:
        """Requests per second."""
        return self.total_requests / self.total_time if self.total_time > 0 else 0

    @property
    def avg_response_time(self) -> float:
        """Average response time in ms."""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0

    @property
    def p50(self) -> float:
        """50th percentile (median) response time."""
        return self._percentile(50)

    @property
    def p95(self) -> float:
        """95th percentile response time."""
        return self._percentile(95)

    @property
    def p99(self) -> float:
        """99th percentile response time."""
        return self._percentile(99)

    def _percentile(self, p: int) -> float:
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * p / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def print_summary(self):
        """Print formatted test results."""
        print(f"\n{'─' * 50}")
        print(f"  {self.test_name}")
        print(f"{'─' * 50}")
        print(f"  Total Requests:    {self.total_requests}")
        print(f"  Successful:        {self.successful} ({self.successful/self.total_requests*100:.1f}%)")
        print(f"  Failed:            {self.failed} ({self.failed/self.total_requests*100:.1f}%)")
        print(f"  Total Time:        {self.total_time:.2f}s")
        print(f"  Requests/sec:      {self.rps:.2f}")
        print(f"{'─' * 50}")
        print(f"  Response Times:")
        print(f"    Average:         {self.avg_response_time:.2f}ms")
        print(f"    P50 (median):    {self.p50:.2f}ms")
        print(f"    P95:             {self.p95:.2f}ms")
        print(f"    P99:             {self.p99:.2f}ms")
        print(f"{'─' * 50}")
        print(f"  Status Codes:")
        for code, count in sorted(self.status_codes.items()):
            print(f"    {code}: {count}")
        if self.errors:
            print(f"{'─' * 50}")
            print(f"  Errors (first 5):")
            for error in self.errors[:5]:
                print(f"    - {error}")


def make_request(
    url: str,
    method: str = "GET",
    data: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: float = 10.0
) -> RequestResult:
    """Make a single HTTP request."""
    start_time = time.perf_counter()
    
    try:
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        
        body = json.dumps(data).encode("utf-8") if data else None
        
        request = urllib.request.Request(
            url,
            data=body,
            headers=req_headers,
            method=method
        )
        
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_time = (time.perf_counter() - start_time) * 1000
            return RequestResult(
                success=True,
                status_code=response.status,
                response_time=response_time
            )
    
    except urllib.error.HTTPError as e:
        response_time = (time.perf_counter() - start_time) * 1000
        # 3xx redirects and 4xx client errors are still "successful" HTTP responses
        return RequestResult(
            success=e.code < 500,
            status_code=e.code,
            response_time=response_time,
            error=str(e) if e.code >= 500 else None
        )
    
    except urllib.error.URLError as e:
        response_time = (time.perf_counter() - start_time) * 1000
        return RequestResult(
            success=False,
            status_code=0,
            response_time=response_time,
            error=f"URLError: {e.reason}"
        )
    
    except Exception as e:
        response_time = (time.perf_counter() - start_time) * 1000
        return RequestResult(
            success=False,
            status_code=0,
            response_time=response_time,
            error=f"{type(e).__name__}: {str(e)}"
        )


def run_load_test(
    test_name: str,
    request_fn: Callable[[], RequestResult],
    total_requests: int,
    concurrent: int
) -> TestResults:
    """Run a load test with the given parameters."""
    results = TestResults(test_name=test_name)
    results.total_requests = total_requests
    
    print(f"\n  Running: {test_name}")
    print(f"  Requests: {total_requests}, Concurrent: {concurrent}")
    print(f"  ", end="", flush=True)
    
    completed = 0
    lock = threading.Lock()
    
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(request_fn) for _ in range(total_requests)]
        
        for future in as_completed(futures):
            result = future.result()
            
            with lock:
                if result.success:
                    results.successful += 1
                else:
                    results.failed += 1
                    if result.error:
                        results.errors.append(result.error)
                
                results.response_times.append(result.response_time)
                results.status_codes[result.status_code] += 1
                
                completed += 1
                if completed % (total_requests // 10) == 0:
                    print("▓", end="", flush=True)
    
    results.total_time = time.perf_counter() - start_time
    print(" Done!")
    
    return results


def random_url() -> str:
    """Generate a random URL for testing."""
    path = ''.join(random.choices(string.ascii_lowercase, k=10))
    return f"https://example.com/{path}"


def main():
    parser = argparse.ArgumentParser(description="Load test URL Shortener API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL")
    parser.add_argument("--requests", type=int, default=1000, help="Total requests per test")
    parser.add_argument("--concurrent", type=int, default=100, help="Concurrent requests")
    parser.add_argument("--short-code", default=None, help="Short code for redirect test")
    parser.add_argument("--skip-create", action="store_true", help="Skip URL creation test")
    parser.add_argument("--skip-redirect", action="store_true", help="Skip redirect test")
    args = parser.parse_args()
    
    base_url = args.url.rstrip("/")
    
    print("\n" + "=" * 50)
    print("  URL SHORTENER LOAD TEST")
    print("=" * 50)
    print(f"  Target: {base_url}")
    print(f"  Requests per test: {args.requests}")
    print(f"  Concurrency: {args.concurrent}")
    
    all_results: list[TestResults] = []
    created_short_code = args.short_code
    
    # Test 1: Health check / Root endpoint
    print("\n" + "=" * 50)
    print("  TEST 1: Health Check (GET /)")
    print("=" * 50)
    
    results = run_load_test(
        test_name="GET / (Health Check)",
        request_fn=lambda: make_request(f"{base_url}/"),
        total_requests=min(args.requests, 500),
        concurrent=args.concurrent
    )
    results.print_summary()
    all_results.append(results)
    
    # Test 2: Create URL (POST)
    if not args.skip_create:
        print("\n" + "=" * 50)
        print("  TEST 2: Create URL (POST /api/v1/urls/)")
        print("=" * 50)
        
        def create_url_request():
            return make_request(
                f"{base_url}/api/v1/urls/",
                method="POST",
                data={"original_url": random_url()}
            )
        
        results = run_load_test(
            test_name="POST /api/v1/urls/ (Create URL)",
            request_fn=create_url_request,
            total_requests=args.requests // 2,  # Fewer writes
            concurrent=args.concurrent // 2
        )
        results.print_summary()
        all_results.append(results)
        
        # Get a short code for redirect test
        if not created_short_code:
            try:
                req = urllib.request.Request(
                    f"{base_url}/api/v1/urls/",
                    data=json.dumps({"original_url": "https://example.com/test"}).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    created_short_code = data.get("short_code")
                    print(f"\n  Created short_code for redirect test: {created_short_code}")
            except Exception as e:
                print(f"\n  Warning: Could not create short_code: {e}")
    
    # Test 3: Redirect (GET /{short_code})
    if not args.skip_redirect and created_short_code:
        print("\n" + "=" * 50)
        print(f"  TEST 3: Redirect (GET /{created_short_code})")
        print("=" * 50)
        
        def redirect_request():
            return make_request(f"{base_url}/{created_short_code}")
        
        results = run_load_test(
            test_name=f"GET /{created_short_code} (Redirect)",
            request_fn=redirect_request,
            total_requests=args.requests,
            concurrent=args.concurrent
        )
        results.print_summary()
        all_results.append(results)
    elif not args.skip_redirect:
        print("\n  Skipping redirect test: No short_code available")
        print("  Use --short-code <code> to specify one")
    
    # Final Summary
    print("\n" + "=" * 50)
    print("  FINAL SUMMARY")
    print("=" * 50)
    
    total_requests = sum(r.total_requests for r in all_results)
    total_successful = sum(r.successful for r in all_results)
    total_time = sum(r.total_time for r in all_results)
    
    print(f"\n  Total Requests:     {total_requests}")
    print(f"  Total Successful:   {total_successful} ({total_successful/total_requests*100:.1f}%)")
    print(f"  Total Time:         {total_time:.2f}s")
    print(f"  Overall RPS:        {total_requests/total_time:.2f}")
    
    print("\n  Per-Test RPS:")
    for r in all_results:
        print(f"    {r.test_name}: {r.rps:.2f} RPS")
    
    print("\n" + "=" * 50)
    print("  Load test complete!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()

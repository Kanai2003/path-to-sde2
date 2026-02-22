#!/usr/bin/env python3
"""
High-performance redirect load test for URL Shortener.
Target: 1000+ requests per second using provided short codes.

No external dependencies - uses only Python standard library.
"""

import argparse
import random
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Optional

# All short codes from the database
SHORT_CODES = [
    "uAo8pb", "XyQeTZ", "doJW0b", "GKW3d2", "x3Aiws", "8fIQSq", "m62G1T", "d2SkRT",
    "qR2v8o", "MptJEX", "x78Vsl", "w11Gmz", "yK1Lt4", "NgKEgz", "rYbLaK", "XXbmtb",
    "ZpnVbP", "c8xY0U", "0KBKwh", "geUu0D", "yQGlXz", "N3j7rF", "UwpBV9", "PCtME5",
    "LV742f", "WEA41Z", "Jw62kv", "Q9NKX0", "qZWpzG", "GjQRQi", "GWqup5", "axlwam",
    "aT2Luo", "beNHEJ", "hpF5Lh", "KGQP0Z", "ZO70HI", "We3yoe", "m7R7RK", "wEqXF3",
    "WOELwZ", "EAxla6", "2lC9A0", "MG0rba", "R7jYt2", "5Mfcfy", "ri1Zjm", "gxrXRm",
    "aE9OzO", "w3AESB", "KrqnKP", "erG4A2", "BIiYPw", "eSWm8P", "QYuIvb", "1nsYna",
    "k0GbCP", "qk1CYs", "rKWE2M", "ri5LSf", "uPMK1a", "4AOwQ9", "2FTNul", "VoCwUO",
    "ChF563", "WP879E", "oxwoFn", "ayY3fO", "0zhXq7", "dgsI2N", "SBzTLf", "MzOehq",
    "gKMNjj", "xvizYS", "0RWN1G", "Qz23Mb", "oolpbq", "o330nW", "rDqTaV", "R9gsZG",
    "vurI22", "2CTqy9", "Vp2oDV", "OxDmht", "8wtkoX", "pbOOq8", "piy4E8", "PQnoyR",
    "YnQfid", "ul2lo7", "VVKXTB", "b2DOaS", "XWUxAZ", "hfu4gG", "axo3wO", "DppkIC",
    "7vloFR", "VOLO6i", "sI1nTR", "cNRE3W", "W9uMPO", "YO20pl", "7dbxkd", "GUKht8",
    "l5QcVm", "YFEBXe", "dgDbQM", "JsSByR", "xOik0o", "7KOkzy", "LCmhFd", "Iepu27",
    "nmDhZR", "77Nr6K", "rQh2lf", "VnlTF7", "n7GxZz", "t4eRTK", "wxKfUB", "ecyN2B",
    "xL5Pza", "rmIX17", "2HaXaG", "2G9Um5", "DGDUxQ", "XxyUrK", "klpnIy", "U8t5k3",
    "oZ4QX8", "zg7DuP", "CEbRqi", "Xwy6jh", "yWcsSl", "pXRU7m", "Njeshx", "DMxGYU",
    "gHaKaz", "Wf40G0", "2aoWQO", "ydM2If", "UvEZMe", "QNcybE", "RGbWgD", "6frtcu",
    "GODQpM", "k8nfRN", "f96H7n", "WwWLQI", "zIO0fP", "5muzHN", "7pUJMR", "dm0boc",
    "BvVe1g", "oNrYn9", "ZqSPDn", "yDEJFg", "7GfBgl", "fyTvHG", "MxY08y", "eYd784",
    "DitQlm", "D1HKwb", "WhitN7", "odTRsR", "OrUHOf", "7sH5yf", "JkrO3d", "8l8e69",
    "UIuM9K", "rRqMxC", "Hq3j3Q", "sySWc0", "zJoKFI", "Dj4oIY", "M7rUDj", "FjPk8u",
    "Icvr5d", "Q7hm0E", "5d9szE", "x7hAZM", "VNhKDv", "tUUwIZ", "XxldYy", "a4y0Vs",
    "nARf9F", "0bgFYN", "0UJYor", "MypdfX", "rjy4vv", "3CZi2g", "O18bMQ", "nOb6Pp",
    "3zHcJO", "FWGaFk", "MHaxVh", "JrfmcP", "zyPgKg", "Ed3VwQ", "mQmNRo", "dFzRJi",
    "YPvl1X", "NrF9p1", "RVFoBm", "ekdkD7", "tXgROF", "pgo6A0", "1pVrNX", "z3y4KN",
    "cHErJP", "YJRamz", "x8cekf", "iFpBgZ", "ZD3ESn", "OwToCz", "lXEpoB", "0G2DJJ",
    "vn6BzU", "N6Gvxw", "SUVlcd", "m6Ueux", "FwAzJK", "mraBZq", "4BxcXc", "27StLP",
    "tv3My5", "owday3", "JC6pB6", "5QR7xE", "S46Ekl", "Cqq8Zs", "bRzvnp", "wj911E",
    "U77LW1", "Wz5AsW", "P9EAXy", "YJqGVw", "3e8KlA", "582nBx", "XE8qoB", "bm6bsD",
    "T0gn6Q", "tOhPhd", "BiCwZR", "nSQfAv", "4CKRZr", "cQSN4M", "Ud27sM", "PSSSKY",
    "MDiJZm", "NewAwQ", "u20Uyj", "CAlI6l", "Q6z6Zn", "LtDRDp", "qc8cLx", "CmU0xU",
    "jITrRr", "M0mdtk", "1fMp4t", "Ixz4Zl", "gR5Y5f", "zsIBBk", "TP6lfA", "3lnF4I",
    "kKeEiS", "fXJvHa", "Zudutt", "G11DAN", "aWPknI", "xqMtTJ", "7VLsXD", "JR7fnK",
    "ftbTqV", "S9UIvl", "v1snjE", "Ut1oL1", "TcpBK9", "h0m607", "jn8LGP", "3COQKz",
    "VRnBip", "yJKUBa", "TI5hsq", "UctByP", "DgyXX4", "eLkU21", "IMoWjK", "tLM9Ww",
    "SqKyrC", "peCVVb", "uqXEnE", "52r9lQ", "Cc5xkZ", "EzNeKC", "ClyQFX", "IykQin",
    "l8TbwV", "ldk14b", "1qKvb9", "YufQrp", "B2IXeI", "j4sIMN", "CKw2HT", "dRWQY7",
    "GsXrNY", "0uoTs5", "HSU3RM", "REYrH6", "uE4iYG", "gIvjRi", "7BLxqg", "D82Slf",
    "U9RFX4", "bwKQND", "kenkrd", "7yi8UI", "8XMHUL", "akQuxk", "qO7u8O", "jhZJfC",
    "bdqDk6", "T468Yo", "ctW1dK", "WkSpjp", "OSFihI", "P0M1l2", "1BUgVy", "IvT8EG",
    "zGT6hX", "qtyt50", "2ImUV2", "XKuKx8", "3F7qSD", "MMZLV9", "reCGHx", "RvNngF",
    "hIr3BL", "kf5vyZ", "uo5JMl", "VnITv7", "0H2WuH", "JeUyz5", "QAoXJw", "CwCysK",
    "yuYrL6", "PV9Ql1", "gkyAtc", "qxnJTl", "vcHI3P", "hhTLzL", "6nks6D", "dVCdKi",
    "kXsy6S", "br41hT", "QkVSai", "bvYDQK", "kWPQ4g", "Y9li5c", "J7dpy3", "mrq9e3",
    "tbZiIr", "SA0Dpu", "o2dfXc", "47TIWE", "ql1Pbn", "4H5vX3", "GFY4ZM", "YwtPUK",
    "GnB0Dh", "ibi82J", "lFBkrH", "WZAzft", "76FG2T", "YeyIP5", "JgZxBW", "zAlevj",
    "JhUrjw", "FAmy4j", "OPDiwp", "7goDBg", "zhePFp", "6Q4Kg0", "zv6Ben", "4S11Xq",
    "Vb8zLW", "EPoBYI", "G52xoY", "hzlwC2", "VY9cy5", "6x8edR", "ebjyPd", "yPmi7o",
    "y0k6bf", "TDXkHe", "aUzzP6", "CI7Aid", "5rDpqi", "qvc089", "bvL7TG", "st4ska",
    "dfSujE", "zPAFME", "VKkfJS", "QnynhS", "mRwmbZ", "lxe4YU", "fk6pZX", "WT6bkP",
    "cDhZeX", "1bl4vm", "Rmrdrw", "nibtWy", "N7FVNJ", "WXGHde", "ZHU4R6", "Wpngnm",
    "NiBCVF", "gNYevY", "lCQAlS", "FZFpzk", "69bJos", "cuaYfx", "5DsFj7", "rl5jrd",
    "sN1tvT", "z5xHRY", "2QkE47", "EX1mE3", "XLt703", "m4GdDs", "ljBJus", "sQqV6Z",
    "GpVNqK", "t9KaPq", "dpEj39", "hmBQ7k", "HmJwPU", "1xe8Tf", "hdy8ja", "Tm8SwS",
    "YmLOs0", "rqc2te", "unESI3", "TwR9LM", "nW1O2I", "7KJN8Q", "iDKnGj", "cA085M",
    "vOSU2d", "LWSZeP", "fdXglx", "Vaboe9", "j9hYfl", "ONGKMN", "HvMebO", "JeV3M7",
    "0XyFqY", "eXQ5Qp", "Zhj2vN", "ydcXk6", "5ziCRa", "6sVI7g", "VONird", "r5bQX1",
    "mIOhS2", "PUizVS", "PDCpIS", "3I7HX8", "RVKfc7", "UeiWg1", "F510gv", "5fLWii",
    "L6d3PV", "oFfURN", "hKs5qp", "XZ7dKg", "pbeaDa", "tk0nGI", "R5rFdm", "xwGXPj",
    "CRJYAF", "PUXMQe", "Qw5CF3", "59y2g7", "sIMmLE", "aYBEpD", "SC9Xb1", "imMn3S",
    "fFOeNo", "fqcMDg", "l1DcLa", "8TIx85", "l12ftY", "szG5u6", "zewmRo", "WBKwER",
    "EOr6zn", "6ILxP2", "7Wo4eT", "SOXzXG", "ecc2gR", "E10EQZ", "k3EUVC"
]


@dataclass
class TestResults:
    """Test results with statistics."""
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    total_time: float = 0
    response_times: list = field(default_factory=list)
    errors: dict = field(default_factory=dict)
    
    @property
    def rps(self) -> float:
        return self.total_requests / self.total_time if self.total_time > 0 else 0
    
    @property
    def success_rate(self) -> float:
        return (self.successful / self.total_requests * 100) if self.total_requests > 0 else 0
    
    def percentile(self, p: int) -> float:
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * p / 100)
        return sorted_times[min(idx, len(sorted_times) - 1)]


def make_redirect_request(url: str, timeout: float = 5.0) -> tuple[bool, float, Optional[str]]:
    """Make a single redirect request. Returns (success, response_time_ms, error)."""
    start = time.perf_counter()
    try:
        request = urllib.request.Request(url, method="GET")
        # Don't follow redirects - we just want to test the redirect response
        opener = urllib.request.build_opener(NoRedirectHandler())
        response = opener.open(request, timeout=timeout)
        response_time = (time.perf_counter() - start) * 1000
        return (response.status in [200, 301, 302, 307, 308], response_time, None)
    except urllib.error.HTTPError as e:
        response_time = (time.perf_counter() - start) * 1000
        if e.code in [301, 302, 307, 308]:
            return (True, response_time, None)
        return (False, response_time, f"HTTP {e.code}")
    except Exception as e:
        response_time = (time.perf_counter() - start) * 1000
        return (False, response_time, str(e)[:50])


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Handler that doesn't follow redirects."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def run_load_test(
    base_url: str,
    total_requests: int,
    concurrent: int,
    duration: Optional[float] = None
) -> TestResults:
    """Run high-performance load test."""
    results = TestResults()
    lock = threading.Lock()
    stop_event = threading.Event()
    
    # Pre-generate all URLs for speed
    urls = [f"{base_url}/{random.choice(SHORT_CODES)}" for _ in range(total_requests)]
    
    completed = [0]
    
    def worker(url: str) -> None:
        if stop_event.is_set():
            return
        
        success, response_time, error = make_redirect_request(url)
        
        with lock:
            if success:
                results.successful += 1
            else:
                results.failed += 1
                if error:
                    results.errors[error] = results.errors.get(error, 0) + 1
            results.response_times.append(response_time)
            completed[0] += 1
    
    print(f"\n{'='*60}")
    print(f"  REDIRECT LOAD TEST - Target: 1000+ RPS")
    print(f"{'='*60}")
    print(f"  URL: {base_url}")
    print(f"  Short codes: {len(SHORT_CODES)}")
    print(f"  Total requests: {total_requests}")
    print(f"  Concurrent connections: {concurrent}")
    print(f"{'='*60}")
    print(f"\n  Progress: ", end="", flush=True)
    
    start_time = time.perf_counter()
    
    # Set timer if duration specified
    if duration:
        timer = threading.Timer(duration, stop_event.set)
        timer.start()
    
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(worker, url) for url in urls]
        
        last_progress = 0
        for future in as_completed(futures):
            if stop_event.is_set():
                break
            progress = completed[0] * 100 // total_requests
            if progress >= last_progress + 10:
                print("█", end="", flush=True)
                last_progress = progress
    
    results.total_time = time.perf_counter() - start_time
    results.total_requests = completed[0]
    
    if duration:
        timer.cancel()
    
    print(" Done!\n")
    
    return results


def print_results(results: TestResults):
    """Print formatted results."""
    print(f"{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Total Requests:     {results.total_requests:,}")
    print(f"  Successful:         {results.successful:,} ({results.success_rate:.1f}%)")
    print(f"  Failed:             {results.failed:,}")
    print(f"  Total Time:         {results.total_time:.2f}s")
    print(f"{'='*60}")
    print(f"  ⚡ REQUESTS/SEC:    {results.rps:,.2f}")
    print(f"{'='*60}")
    print(f"  Response Times:")
    print(f"    Min:              {min(results.response_times):.2f}ms")
    print(f"    Avg:              {sum(results.response_times)/len(results.response_times):.2f}ms")
    print(f"    P50 (median):     {results.percentile(50):.2f}ms")
    print(f"    P95:              {results.percentile(95):.2f}ms")
    print(f"    P99:              {results.percentile(99):.2f}ms")
    print(f"    Max:              {max(results.response_times):.2f}ms")
    
    if results.errors:
        print(f"{'='*60}")
        print(f"  Errors:")
        for error, count in sorted(results.errors.items(), key=lambda x: -x[1])[:5]:
            print(f"    {error}: {count}")
    
    print(f"{'='*60}")
    
    # Performance verdict
    if results.rps >= 1000:
        print(f"  ✅ TARGET ACHIEVED: {results.rps:,.0f} RPS >= 1000 RPS")
    else:
        print(f"  ❌ TARGET NOT MET: {results.rps:,.0f} RPS < 1000 RPS")
        print(f"     Try increasing --concurrent or check server performance")
    
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="High-performance redirect load test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic test (10K requests, 500 concurrent)
  python scripts/redirect_load_test.py

  # High concurrency test
  python scripts/redirect_load_test.py --concurrent 1000 --requests 50000

  # Different server
  python scripts/redirect_load_test.py --url http://localhost:8080
        """
    )
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL")
    parser.add_argument("--requests", "-n", type=int, default=10000, help="Total requests")
    parser.add_argument("--concurrent", "-c", type=int, default=500, help="Concurrent connections")
    parser.add_argument("--duration", "-d", type=float, default=None, help="Max duration in seconds")
    args = parser.parse_args()
    
    results = run_load_test(
        base_url=args.url.rstrip("/"),
        total_requests=args.requests,
        concurrent=args.concurrent,
        duration=args.duration
    )
    
    print_results(results)


if __name__ == "__main__":
    main()

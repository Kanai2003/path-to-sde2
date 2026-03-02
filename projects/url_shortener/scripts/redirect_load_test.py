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
    "bYsawo", "SudFGs", "uCYFsM", "0kDSmt", "vu0efz", "zzkPKA", "tR7Vdc", "QHCwaJ",
    "NAJxo2", "cZ0xdj", "JoTuPk", "IbCZ49", "raQ1al", "tqRaMy", "raWftV", "2NJswf",
    "bLgpSQ", "rEdvNN", "PGSUTX", "Z10Wbk", "XYJNqG", "Va1lHf", "aeKbU1", "hnVyPb",
    "cabRmW", "3lPIRm", "8mbi8g", "e9WDmk", "2eQSNb", "k8RzA4", "2VyjZF", "zgq0kY",
    "pR6mWZ", "qTgiK8", "7jlkev", "0Lx8XA", "yRODCi", "Vd3706", "FMdyjq", "BGCrVD",
    "yJq9lf", "bOTp9G", "pq6KPK", "bYk7eZ", "65GuMz", "nSfDZv", "tdW5mf", "3I84E4",
    "KweGAv", "l9uNea", "45LSkx", "Cz8VTb", "tDSFrI", "JQ7vPh", "PbXgnd", "lEbtMj",
    "BOCBcL", "4A0VC5", "p8P3UY", "UXVOVv", "SD4ReO", "4XMnR5", "hnC8XO", "zyzdYp",
    "ajbCEp", "XmXG6Z", "skcmVk", "QhiING", "zBoVow", "NUvA0o", "O8VtPP", "OVwn9W",
    "NdRe6W", "JP5Duj", "j1NGAR", "UgBYqm", "FNEfwG", "atb13Z", "YtDzJf", "X3idKW",
    "EvTxSn", "55HIEu", "EkT17R", "8N70si", "KB99qe", "Cv7e1T", "O8YnB5", "XzlMIU",
    "Qlnbu9", "z47LOt", "7bfybY", "jKRrbN", "d5eZbd", "sGr6Ox", "cIFj2w", "ijWwGv",
    "s4NEXn", "K3PL8L", "x9OJZO", "aTxsK0", "gs8XGy", "SgHjEb", "B0Xfk7", "kyhS8X",
    "610qPG", "bKc7Nx", "uk387v", "2wYvmx", "k3EUVC", "VAVdZc", "QFZg3D", "WWnm39",
    "EIXQBN", "U1WhHz", "KC1GPy", "LUODQQ", "hVeK3k", "3ZqMTu", "PpDyxz", "GoxezY",
    "M6rVn5", "6ERcJF", "cpnnQs", "VyKsCR", "Pm76fY", "qzaF7A", "PA6TlG", "WPIHZ0",
    "Mi7BbD", "6Ha1BF", "GiIzyp", "5JzzoU", "RqJYHw", "xQffNn", "MfnZUd", "Of22iR",
    "6xehOY", "a66owd", "h9u7ui", "SfY8ub", "qA2o9B", "XAC7rz", "dk0KxV", "6DrtAc",
    "memOWC", "G78NFF", "58lVKd", "eHRK3h", "jlTPxu", "1SEanD", "df1h48", "skQwHV",
    "ZeJMYU", "JERaDz", "gWWw7w", "6ToZpz", "7xQAoG", "juymeD", "QtfcM7", "NgkpI6",
    "1Wcfxj", "CIgeet", "JvTnjj", "D5wsm3", "xPghfZ", "C6fVFR", "JXBS8M", "xBiEJm",
    "TxaoZS", "JayWGA", "ixVEXw", "ovsn6E", "F25x4B", "FgRw5H", "cgHdMg", "sD2wVc",
    "xmuEP5", "MlwwIs", "ic9Yyg", "qPATcB", "DNkDYS", "1wBa6W", "N4akJv", "RI3jdZ",
    "FZPpp2", "Lm5hfh", "n7U6D6", "ZOSz78", "e7iYFD", "SNTxmY", "OXnDcd", "bv0baQ",
    "rfJLpX", "6nslKF", "sTomUM", "W8gInV", "6mGQix", "anLvUB", "HUip0c", "Eat6Ak",
    "L7Qn8V", "DsXB26", "8FtFjY", "E1qU0i", "W72lex", "FLttRS", "3kzFit", "QZPoNO",
    "Dcobly", "e4uxD2", "Q6Ol1C", "VZcS6K", "8mKUHW", "fMbkZP", "F9reXB", "hqh4LD",
    "fILpU7", "GT2mLi", "LyLPX4", "WJ7h1B", "WzkDTQ", "1VkacB", "bkaJyv", "PEZIDe",
    "SbMZAx", "d5ikIi", "TU8Fjr", "jc3cJ2", "YYybDI", "VJ5DMV", "0EI8Df", "VPJp60",
    "TvVlkZ", "mmkNGo", "sYl2eZ", "uZo5Nr", "WBPneE", "u1CJt7", "46F2wt", "o5E9l8",
    "wKZb4t", "cp35zD", "65l9su", "WcP9qQ", "WBjdzx", "xU9Xeh", "br6itA", "Zi0a8d",
    "2YWMTt", "dzbZA6", "Ww7N11", "hidlZC", "707gHu", "NSze2v", "vHlULq", "DounBA",
    "t1s7uM", "WIe4nL", "KHgkqx", "QliIYV", "l4JfjM", "iW3Pn1", "gEXA5n", "DQ4lI4",
    "D5SCE6", "GziEP4", "V90wJL", "6q4AG5", "NSum5Q", "C6mZRW", "mYEcnu", "VRYasl",
    "XASSL3", "7JCGlE", "6QdKCP", "l7Y4JQ", "jRdtIe", "jwCqlQ", "W8pygq", "p2HtHQ",
    "6eXY5C", "UTrWy6", "PxxjIt", "zcDo3E", "tuFxrb", "DwJig8", "4bl2Nm", "qv7Zx2",
    "iCzcCx", "5Ee7nb", "eAxumv", "7SabPD", "X5Oe2m", "hyNFB3", "jNa5A6", "h8RcX1",
    "j7sEhe", "GWyVWu", "qmb98z", "BDPmL4", "fATSfI", "ETAFvf", "TN6DF4", "RqaESd",
    "oSDozl", "svXcdU", "z9LrUa", "tdT1ZA", "qwrc8a", "zRoyMy", "tGg4y2", "PplEzk",
    "bXzNRM", "OMfGzM", "dIrxBv", "hBnCyK", "NjHZCk", "1VOGH5", "ZgDqfM", "DnMGKy",
    "Y034Gj", "tB3f9B", "P2N98i", "Q2TO32", "4SKpUo", "p7ostL", "Sl8B3W", "xeMQAe",
    "530FpH", "1qNwGi", "iCl5xa", "U3PNEn", "YkPMXd", "EY9bBq", "l1l1Px", "qffjLJ",
    "aUxNcq", "rOOPZh", "Hfs2gJ", "FXsVQi", "g43xbY", "fRuqgo", "1N6jlO", "saUXjm",
    "qZY5M8", "c6gRgp", "RnZ1rt", "aa5voA", "tgKkSO", "JUt3Tz", "5GVwld", "PXudyK",
    "z3lTed", "1wEuZ7", "jZYId4", "35QoEj", "U1T4A1", "54faqZ", "1ZefKu", "K44eI6",
    "NkFHXX", "iTVQWL", "mUNkOT", "MTAsI8", "ksNlJG", "3wiBk6", "St153Y", "c5ubDV",
    "HAjZyz", "Cs2Lpk", "BgrP0l", "kMqKTk", "X9SNI6", "tfySZw", "m7mdAk", "rGP5JB",
    "ZTFxz9", "JoGAan", "aIYVnC", "IC330m", "Pbma7o", "2yak72", "6VX1H0", "jHkccX",
    "jCti3x", "jsCnu4", "PKYsyV", "ch9FRj", "f1qcKV", "FoJpAI", "SSGxGO", "kRF2cF",
    "3nFr7e", "xH8EYf", "Cf41oy", "gto8Up", "cn648N", "jKIxBq", "J5hW6d", "fqn8fZ",
    "Zdq050", "lShKjq", "67lxOt", "I8vTww", "fOjwda", "sBfNDW", "tXbl97", "SrxCp8",
    "w19FvT", "XVT3kt", "OyDxkf", "P5fwK9", "ntENPY", "1UPnH0", "DaAvYz", "MuFUAe",
    "p1UCtc", "uHS1Q8", "zrCNP6", "LqZo11", "QRpNTk", "rYiljl", "S6kawu", "ulCpem",
    "zSrI0J", "EGqyAU", "QXI8xG", "DGXzT0", "UTnnvh", "jseduc", "hJfMEc", "DLFSsm",
    "HEmrPY", "d1xWT8", "rEMgAU", "lH45mr", "PIKMG3", "ae8rpq", "lgIONH", "HXIG4G",
    "Daww60", "0Su5lL", "2yqFyU", "E3whdH", "bAa9Pi", "egmlQK", "Dkyt3a", "cgCwjZ",
    "VUNOOY", "eokyKL", "oZe7x6", "XkzCXe", "RMlzzJ", "gch0DO", "ERTv2N", "l1qnRJ",
    "mHj7fg", "64skaE", "cJmbir", "CwsNT2", "hWTATy", "ObFsu0", "ddgCUi", "Q3IspF",
    "f3HZbl", "jbcD53", "0xb4F1", "d4FGW2", "d6C36h", "eq8Kng", "tHBEvS", "nhoRm8",
    "qzQLCv", "RURY4B", "Ngm5VO", "2csbJI", "5H8Zf9", "ypEVQj", "eLCa9r", "f7G0CP",
    "sZjOZQ", "bSrscU", "ifDgO1", "Jr80MR", "Q39OdE", "0LwZES", "G3w3mz", "thkoWv",
    "KZBzXb", "RPVEUb", "bYMjVq", "YzHMFG", "5ns85r", "nX5tVn", "hmDHsT", "cUI0kx",
    "igsFeR", "K0jkNF", "dLIXcT", "XsW40J", "QcnVKE", "gu9xdA"
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
        return (
            (self.successful / self.total_requests * 100)
            if self.total_requests > 0
            else 0
        )

    def percentile(self, p: int) -> float:
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * p / 100)
        return sorted_times[min(idx, len(sorted_times) - 1)]


def make_redirect_request(
    url: str, timeout: float = 5.0
) -> tuple[bool, float, Optional[str]]:
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
    duration: Optional[float] = None,
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
    print("  REDIRECT LOAD TEST - Target: 1000+ RPS")
    print(f"{'='*60}")
    print(f"  URL: {base_url}")
    print(f"  Short codes: {len(SHORT_CODES)}")
    print(f"  Total requests: {total_requests}")
    print(f"  Concurrent connections: {concurrent}")
    print(f"{'='*60}")
    print("\n  Progress: ", end="", flush=True)

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
    print("  RESULTS")
    print(f"{'='*60}")
    print(f"  Total Requests:     {results.total_requests:,}")
    print(f"  Successful:         {results.successful:,} ({results.success_rate:.1f}%)")
    print(f"  Failed:             {results.failed:,}")
    print(f"  Total Time:         {results.total_time:.2f}s")
    print(f"{'='*60}")
    print(f"  ⚡ REQUESTS/SEC:    {results.rps:,.2f}")
    print(f"{'='*60}")
    print("  Response Times:")
    print(f"    Min:              {min(results.response_times):.2f}ms")
    print(
        f"    Avg:              {sum(results.response_times)/len(results.response_times):.2f}ms"
    )
    print(f"    P50 (median):     {results.percentile(50):.2f}ms")
    print(f"    P95:              {results.percentile(95):.2f}ms")
    print(f"    P99:              {results.percentile(99):.2f}ms")
    print(f"    Max:              {max(results.response_times):.2f}ms")

    if results.errors:
        print(f"{'='*60}")
        print("  Errors:")
        for error, count in sorted(results.errors.items(), key=lambda x: -x[1])[:5]:
            print(f"    {error}: {count}")

    print(f"{'='*60}")

    # Performance verdict
    if results.rps >= 1000:
        print(f"  ✅ TARGET ACHIEVED: {results.rps:,.0f} RPS >= 1000 RPS")
    else:
        print(f"  ❌ TARGET NOT MET: {results.rps:,.0f} RPS < 1000 RPS")
        print("     Try increasing --concurrent or check server performance")

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
        """,
    )
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL")
    parser.add_argument(
        "--requests", "-n", type=int, default=10000, help="Total requests"
    )
    parser.add_argument(
        "--concurrent", "-c", type=int, default=500, help="Concurrent connections"
    )
    parser.add_argument(
        "--duration", "-d", type=float, default=None, help="Max duration in seconds"
    )
    args = parser.parse_args()

    results = run_load_test(
        base_url=args.url.rstrip("/"),
        total_requests=args.requests,
        concurrent=args.concurrent,
        duration=args.duration,
    )

    print_results(results)


if __name__ == "__main__":
    main()

"""Simple in-memory per-key rate limiting."""

from __future__ import annotations

import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_per_second: int = 10):
        self.max_per_second = max_per_second
        self.buckets = defaultdict(list)  # api_key -> [timestamps]

    def is_allowed(self, api_key: str) -> bool:
        now = time.time()
        self.buckets[api_key] = [t for t in self.buckets[api_key] if now - t < 1.0]

        if len(self.buckets[api_key]) >= self.max_per_second:
            return False

        self.buckets[api_key].append(now)
        return True


rate_limiter = RateLimiter(max_per_second=10)

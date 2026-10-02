import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, status
from app.core.config import settings

class RateLimiter:
    def __init__(self):
        # Maps key -> list of timestamp floats
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self.window_seconds = 24 * 3600  # 24 hours

    def check_rate_limit(self, key: str, max_requests: int = None, label: str = "generation"):
        if max_requests is None:
            max_requests = settings.RATE_LIMIT_PER_DAY

        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old timestamps
        timestamps = [ts for ts in self._requests[key] if ts > cutoff]
        self._requests[key] = timestamps

        if len(timestamps) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily {label} quota exceeded ({max_requests} per day). Please try again tomorrow.",
                headers={"Retry-After": "86400"},
            )

        self._requests[key].append(now)

    def get_usage_count(self, key: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        return len([ts for ts in self._requests[key] if ts > cutoff])

rate_limiter = RateLimiter()

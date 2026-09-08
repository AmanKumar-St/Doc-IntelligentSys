import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional

from app.core.config import get_settings


@dataclass
class RateLimitBucket:
    requests: list[float] = field(default_factory=list)
    lock: Lock = field(default_factory=Lock)

    def add_request(self, now: float) -> None:
        with self.lock:
            self.requests.append(now)

    def get_request_count(self, window_start: float) -> int:
        with self.lock:
            return sum(1 for t in self.requests if t >= window_start)

    def cleanup_old_requests(self, window_start: float) -> None:
        with self.lock:
            self.requests = [t for t in self.requests if t >= window_start]


class InMemoryRateLimiter:
    def __init__(self):
        self.buckets: dict[str, RateLimitBucket] = defaultdict(RateLimitBucket)
        self.global_lock = Lock()

    def _get_bucket(self, key: str) -> RateLimitBucket:
        with self.global_lock:
            return self.buckets[key]

    def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, dict]:
        now = time.time()
        window_start = now - window_seconds
        bucket = self._get_bucket(identifier)
        bucket.cleanup_old_requests(window_start)
        current_count = bucket.get_request_count(window_start)

        if current_count >= limit:
            oldest_in_window = min((t for t in bucket.requests if t >= window_start), default=now)
            reset_at = oldest_in_window + window_seconds
            return False, {
                "limit": limit,
                "remaining": 0,
                "reset_at": reset_at,
                "retry_after": int(reset_at - now) + 1,
            }

        bucket.add_request(now)
        remaining = limit - current_count - 1
        return True, {
            "limit": limit,
            "remaining": max(0, remaining),
            "reset_at": now + window_seconds,
            "retry_after": 0,
        }


_rate_limiter_instance: Optional[InMemoryRateLimiter] = None


def get_rate_limiter() -> InMemoryRateLimiter:
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = InMemoryRateLimiter()
    return _rate_limiter_instance


class RateLimitExceeded(Exception):
    def __init__(self, message: str, retry_after: int, limit: int, window_seconds: int):
        super().__init__(message)
        self.retry_after = retry_after
        self.limit = limit
        self.window_seconds = window_seconds


async def check_upload_rate_limit(client_ip: str) -> dict:
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return {"limit": 0, "remaining": 0, "reset_at": 0, "retry_after": 0}

    limiter = get_rate_limiter()
    key = f"upload:{client_ip}"
    allowed, info = limiter.check_rate_limit(
        key,
        settings.upload_rate_limit,
        settings.upload_rate_window_seconds,
    )
    if not allowed:
        raise RateLimitExceeded(
            f"Upload rate limit exceeded. Limit: {settings.upload_rate_limit} requests per {settings.upload_rate_window_seconds} seconds.",
            info["retry_after"],
            settings.upload_rate_limit,
            settings.upload_rate_window_seconds,
        )
    return info


async def check_chat_rate_limit(client_ip: str) -> dict:
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return {"limit": 0, "remaining": 0, "reset_at": 0, "retry_after": 0}

    limiter = get_rate_limiter()
    key = f"chat:{client_ip}"
    allowed, info = limiter.check_rate_limit(
        key,
        settings.chat_rate_limit,
        settings.chat_rate_window_seconds,
    )
    if not allowed:
        raise RateLimitExceeded(
            f"Chat rate limit exceeded. Limit: {settings.chat_rate_limit} requests per {settings.chat_rate_window_seconds} seconds.",
            info["retry_after"],
            settings.chat_rate_limit,
            settings.chat_rate_window_seconds,
        )
    return info


async def check_search_rate_limit(client_ip: str) -> dict:
    settings = get_settings()
    if not settings.rate_limit_enabled:
        return {"limit": 0, "remaining": 0, "reset_at": 0, "retry_after": 0}

    limiter = get_rate_limiter()
    key = f"search:{client_ip}"
    allowed, info = limiter.check_rate_limit(
        key,
        settings.search_rate_limit,
        settings.search_rate_window_seconds,
    )
    if not allowed:
        raise RateLimitExceeded(
            f"Search rate limit exceeded. Limit: {settings.search_rate_limit} requests per {settings.search_rate_window_seconds} seconds.",
            info["retry_after"],
            settings.search_rate_limit,
            settings.search_rate_window_seconds,
        )
    return info
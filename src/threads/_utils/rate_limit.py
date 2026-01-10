"""Rate limiting utilities for the Threads SDK."""

import time
from collections import deque
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class RateLimiter:
    """Thread-safe rate limiter using sliding window.

    Tracks requests within a time window to prevent exceeding API limits.
    """

    max_requests: int
    window_seconds: float = 86400.0  # 24 hours default
    _timestamps: deque[float] = field(default_factory=deque)
    _lock: Lock = field(default_factory=Lock)

    def _cleanup_old_timestamps(self, now: float) -> None:
        """Remove timestamps outside the current window."""
        cutoff = now - self.window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

    def can_proceed(self) -> bool:
        """Check if a request can proceed without exceeding limits.

        Returns:
            True if request can proceed, False otherwise.
        """
        with self._lock:
            now = time.time()
            self._cleanup_old_timestamps(now)
            return len(self._timestamps) < self.max_requests

    def record_request(self) -> None:
        """Record that a request was made."""
        with self._lock:
            self._timestamps.append(time.time())

    def wait_if_needed(self) -> float:
        """Wait until a request can proceed.

        Returns:
            Time waited in seconds (0 if no wait needed).
        """
        with self._lock:
            now = time.time()
            self._cleanup_old_timestamps(now)

            if len(self._timestamps) < self.max_requests:
                return 0.0

            oldest = self._timestamps[0]
            wait_time = (oldest + self.window_seconds) - now

            if wait_time > 0:
                time.sleep(wait_time)
                return wait_time

            return 0.0

    @property
    def remaining(self) -> int:
        """Get remaining requests allowed in current window."""
        with self._lock:
            self._cleanup_old_timestamps(time.time())
            return max(0, self.max_requests - len(self._timestamps))

    @property
    def usage(self) -> int:
        """Get current usage count in the window."""
        with self._lock:
            self._cleanup_old_timestamps(time.time())
            return len(self._timestamps)

    def reset(self) -> None:
        """Reset the rate limiter."""
        with self._lock:
            self._timestamps.clear()


class AsyncRateLimiter:
    """Async-compatible rate limiter using sliding window."""

    def __init__(
        self,
        max_requests: int,
        window_seconds: float = 86400.0,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: deque[float] = deque()

    def _cleanup_old_timestamps(self, now: float) -> None:
        """Remove timestamps outside the current window."""
        cutoff = now - self.window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

    def can_proceed(self) -> bool:
        """Check if a request can proceed without exceeding limits."""
        now = time.time()
        self._cleanup_old_timestamps(now)
        return len(self._timestamps) < self.max_requests

    def record_request(self) -> None:
        """Record that a request was made."""
        self._timestamps.append(time.time())

    async def wait_if_needed(self) -> float:
        """Wait until a request can proceed (async version)."""
        import asyncio

        now = time.time()
        self._cleanup_old_timestamps(now)

        if len(self._timestamps) < self.max_requests:
            return 0.0

        oldest = self._timestamps[0]
        wait_time = (oldest + self.window_seconds) - now

        if wait_time > 0:
            await asyncio.sleep(wait_time)
            return wait_time

        return 0.0

    @property
    def remaining(self) -> int:
        """Get remaining requests allowed in current window."""
        self._cleanup_old_timestamps(time.time())
        return max(0, self.max_requests - len(self._timestamps))

    def reset(self) -> None:
        """Reset the rate limiter."""
        self._timestamps.clear()

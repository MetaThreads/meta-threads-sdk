"""Tests for rate limiting utilities."""

from __future__ import annotations

import time

from threads._utils.rate_limit import AsyncRateLimiter, RateLimiter


class TestRateLimiter:
    """Tests for synchronous RateLimiter."""

    def test_initialization(self):
        """Test rate limiter initializes correctly."""
        limiter = RateLimiter(max_requests=100, window_seconds=60.0)

        assert limiter.max_requests == 100
        assert limiter.window_seconds == 60.0
        assert limiter.remaining == 100
        assert limiter.usage == 0

    def test_can_proceed_under_limit(self):
        """Test can_proceed returns True when under limit."""
        limiter = RateLimiter(max_requests=5, window_seconds=60.0)

        assert limiter.can_proceed() is True

    def test_can_proceed_at_limit(self):
        """Test can_proceed returns False when at limit."""
        limiter = RateLimiter(max_requests=2, window_seconds=60.0)

        limiter.record_request()
        limiter.record_request()

        assert limiter.can_proceed() is False

    def test_record_request(self):
        """Test recording requests."""
        limiter = RateLimiter(max_requests=10, window_seconds=60.0)

        assert limiter.usage == 0
        limiter.record_request()
        assert limiter.usage == 1
        limiter.record_request()
        assert limiter.usage == 2

    def test_remaining_count(self):
        """Test remaining count calculation."""
        limiter = RateLimiter(max_requests=5, window_seconds=60.0)

        assert limiter.remaining == 5
        limiter.record_request()
        assert limiter.remaining == 4
        limiter.record_request()
        limiter.record_request()
        assert limiter.remaining == 2

    def test_reset(self):
        """Test resetting the limiter."""
        limiter = RateLimiter(max_requests=5, window_seconds=60.0)

        limiter.record_request()
        limiter.record_request()
        assert limiter.usage == 2

        limiter.reset()
        assert limiter.usage == 0
        assert limiter.remaining == 5

    def test_cleanup_old_timestamps(self):
        """Test that old timestamps are cleaned up."""
        limiter = RateLimiter(max_requests=5, window_seconds=0.1)

        limiter.record_request()
        limiter.record_request()
        assert limiter.usage == 2

        time.sleep(0.15)  # Wait for window to expire

        assert limiter.can_proceed() is True
        assert limiter.usage == 0

    def test_wait_if_needed_no_wait(self):
        """Test wait_if_needed when no wait is needed."""
        limiter = RateLimiter(max_requests=5, window_seconds=60.0)

        result = limiter.wait_if_needed()

        assert result == 0.0

    def test_wait_if_needed_waits(self):
        """Test wait_if_needed actually waits."""
        limiter = RateLimiter(max_requests=1, window_seconds=0.1)
        limiter.record_request()

        start = time.time()
        result = limiter.wait_if_needed()
        elapsed = time.time() - start

        # Should have waited approximately 0.1 seconds
        assert result > 0
        assert elapsed >= 0.05  # Allow some tolerance


class TestAsyncRateLimiter:
    """Tests for asynchronous AsyncRateLimiter."""

    def test_initialization(self):
        """Test async rate limiter initializes correctly."""
        limiter = AsyncRateLimiter(max_requests=100, window_seconds=60.0)

        assert limiter.max_requests == 100
        assert limiter.window_seconds == 60.0
        assert limiter.remaining == 100

    def test_can_proceed_under_limit(self):
        """Test can_proceed returns True when under limit."""
        limiter = AsyncRateLimiter(max_requests=5, window_seconds=60.0)

        assert limiter.can_proceed() is True

    def test_can_proceed_at_limit(self):
        """Test can_proceed returns False when at limit."""
        limiter = AsyncRateLimiter(max_requests=2, window_seconds=60.0)

        limiter.record_request()
        limiter.record_request()

        assert limiter.can_proceed() is False

    def test_record_request(self):
        """Test recording requests."""
        limiter = AsyncRateLimiter(max_requests=10, window_seconds=60.0)

        limiter.record_request()
        assert limiter.remaining == 9
        limiter.record_request()
        assert limiter.remaining == 8

    def test_reset(self):
        """Test resetting the limiter."""
        limiter = AsyncRateLimiter(max_requests=5, window_seconds=60.0)

        limiter.record_request()
        limiter.record_request()
        assert limiter.remaining == 3

        limiter.reset()
        assert limiter.remaining == 5

    def test_cleanup_old_timestamps(self):
        """Test that old timestamps are cleaned up."""
        limiter = AsyncRateLimiter(max_requests=5, window_seconds=0.1)

        limiter.record_request()
        limiter.record_request()
        assert limiter.remaining == 3

        time.sleep(0.15)  # Wait for window to expire

        assert limiter.can_proceed() is True
        assert limiter.remaining == 5

    async def test_wait_if_needed_no_wait(self):
        """Test async wait_if_needed when no wait is needed."""
        limiter = AsyncRateLimiter(max_requests=5, window_seconds=60.0)

        result = await limiter.wait_if_needed()

        assert result == 0.0

    async def test_wait_if_needed_waits(self):
        """Test async wait_if_needed actually waits."""
        limiter = AsyncRateLimiter(max_requests=1, window_seconds=0.1)
        limiter.record_request()

        start = time.time()
        result = await limiter.wait_if_needed()
        elapsed = time.time() - start

        # Should have waited approximately 0.1 seconds
        assert result > 0
        assert elapsed >= 0.05  # Allow some tolerance

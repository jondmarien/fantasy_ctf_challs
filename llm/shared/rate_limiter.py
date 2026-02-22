"""
Per-session rate limiter for LLM CTF challenges.
Uses in-memory storage with cookie-based session tracking.
"""

import os
import time
import uuid
from collections import defaultdict


class RateLimiter:
    """Simple in-memory per-session rate limiter."""

    def __init__(self, max_requests: int | None = None, window_seconds: int = 300):
        self.max_requests = max_requests or int(os.environ.get("RATE_LIMIT", "30"))
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, session_id: str) -> tuple[bool, int]:
        """
        Check if a session is within rate limits.
        Returns (allowed: bool, remaining: int).
        """
        now = time.time()
        cutoff = now - self.window_seconds

        self._requests[session_id] = [
            t for t in self._requests[session_id] if t > cutoff
        ]

        if len(self._requests[session_id]) >= self.max_requests:
            return False, 0

        remaining = self.max_requests - len(self._requests[session_id])
        return True, remaining

    def record(self, session_id: str) -> None:
        """Record a request for a session."""
        self._requests[session_id].append(time.time())

    @staticmethod
    def generate_session_id() -> str:
        """Generate a new session ID."""
        return str(uuid.uuid4())

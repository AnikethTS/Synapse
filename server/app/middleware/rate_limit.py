import time
from collections import deque

from fastapi import HTTPException, Request

from app.core.config import get_settings

_windows: dict[str, deque[float]] = {}


def check_rate_limit(request: Request) -> None:
    """
    Sliding-window rate limiter (per IP).

    Maintains a deque of request timestamps per IP. On each call:
      1. Evict timestamps older than the window from the left — O(k) where k
         is the number of expired entries (amortised O(1) per request).
      2. Reject if the remaining count meets the limit.
      3. Append the current timestamp.

    A periodic sweep removes deques for IPs that have been idle longer than
    one window, bounding memory to O(active IPs × window size).
    """
    cfg = get_settings()
    now = time.monotonic()
    ip = request.client.host if request.client else "unknown"
    window = _windows.setdefault(ip, deque())

    while window and now - window[0] > cfg.rate_limit_window_s:
        window.popleft()

    if len(window) >= cfg.rate_limit_requests:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Rate limit exceeded: max {cfg.rate_limit_requests} requests "
                f"per {cfg.rate_limit_window_s}s."
            ),
        )

    window.append(now)

    if len(_windows) > 10_000:
        stale = [
            k for k, v in _windows.items()
            if not v or now - v[-1] > cfg.rate_limit_window_s
        ]
        for k in stale:
            del _windows[k]

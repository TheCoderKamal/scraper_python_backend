# ===== core/rate_limit.py =====
import time
from collections import defaultdict
from fastapi import HTTPException
from core.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def check_rate_limit(self, api_key: str):
        now = time.time()
        self.requests[api_key] = [
            req_time for req_time in self.requests[api_key]
            if now - req_time < RATE_LIMIT_WINDOW
        ]
        
        if len(self.requests[api_key]) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        self.requests[api_key].append(now)

rate_limiter = RateLimiter()
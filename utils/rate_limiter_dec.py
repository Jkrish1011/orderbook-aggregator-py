from functools import wraps
import time
from decimal import Decimal

class TokenBucketTooEarly(RuntimeError):
    pass

def rate_limiter(capacity: int,tokens_per_minute: float):

    if capacity <= 0:
        raise ValueError("Value must be greater than 0")
    
    if tokens_per_minute <= 0.0:
        raise ValueError("Value must be greater than 0")
    
    tokens_per_second = Decimal(tokens_per_minute / 60.0)

    def decorator(func):
        curr_capacity = Decimal(capacity)
        last_time = time.monotonic()

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_time, curr_capacity
            result = func(*args, **kwargs)
            now = time.monotonic()
            time_elapsed = Decimal(now - last_time)

            if time_elapsed == 0:
                raise TokenBucketTooEarly("time elapsed should be >= 2 min")
            
            if time_elapsed >= 0 and tokens_per_second > 0.0:
                curr_capacity = min(capacity, (time_elapsed * tokens_per_second) + curr_capacity )

            last_time = now
            
            if curr_capacity < 1.0:
                # we have surpassed the time limit
                raise TokenBucketTooEarly("time elapsed should be >= 2 min")

            curr_capacity -= 1.0

            return result
        return wrapper
    return decorator
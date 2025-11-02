from functools import wraps
import time
from decimal import Decimal
import threading

class TokenBucketTooEarly(RuntimeError):
    pass

def rate_limiter(capacity: int, tokens_per_minute: float):

    if capacity <= 0:
        raise ValueError("Value must be greater than 0")
    
    if tokens_per_minute <= 0.0:
        raise ValueError("Value must be greater than 0")
    
    # how many tokens per second to ease calculations
    tokens_per_second = Decimal(tokens_per_minute / 60.0)

    def decorator(func):
        
        curr_capacity = Decimal(capacity)
        # Since no previous request has been made, last_time is None.
        last_time = None

        lock = threading.Lock()

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_time, curr_capacity
            
            with lock:
                now = time.monotonic()
                
                # if this is not the first-call to the function.
                if last_time is not None:
                    time_elapsed = Decimal(now - last_time)
                    curr_capacity = min(Decimal(capacity), curr_capacity + tokens_per_second * time_elapsed)
                
                if curr_capacity < Decimal(1):
                    raise TokenBucketTooEarly("Insufficient tokens. Rate limit exceeded.")
                
                # consume the tokens
                curr_capacity -= Decimal(1)
                last_time = now

            return func(*args, **kwargs)
        return wrapper
    return decorator
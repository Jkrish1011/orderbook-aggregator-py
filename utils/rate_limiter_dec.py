from functools import wraps
import time

def rate_limiter(min_interval: int):

    last_call_time_obj = {}

    def decorator(func):
        func_name = func.__name__
        curr_time = time.time()
        print("func name:", func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if func_name in last_call_time_obj:
                if min_interval + last_call_time_obj[func_name] < curr_time:
                    last_call_time_obj[func_name] = time.time()
                else:
                    time.sleep(curr_time - last_call_time_obj[func_name])
            else:
                last_call_time_obj[func_name] = curr_time
                
            return result
        return wrapper
    return decorator
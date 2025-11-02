import requests
from typing import Dict, Any
from utils.rate_limiter_dec import rate_limiter

# tokens_per_second = 30.0 / 60.0 = 0.5
# after 1 call (consuming 1 token), the logic makes it wait 2 seconds (1 token / 0.5 tokens_per_second) ~ 2 seconds
@rate_limiter(capacity=1, tokens_per_minute=30.0)
def get_coinbase_data(API) -> Dict[str, Any]:
    try:
        response = requests.get(API)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error: {e}")
    
@rate_limiter(capacity=1, tokens_per_minute=30.0)
def get_gemini_data(API) -> Dict[str, Any]:
    try:
        response = requests.get(API)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error: {e}")
    
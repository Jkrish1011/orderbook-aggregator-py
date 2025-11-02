import requests
from typing import Dict, Any
from utils.rate_limiter_dec import rate_limiter

@rate_limiter(capacity=2, tokens_per_minute=1.0)
def get_coinbase_data(API) -> Dict[str, Any]:
    try:
        response = requests.get(API)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error: {e}")
    
@rate_limiter(capacity=2, tokens_per_minute=1.0)
def get_gemini_data(API) -> Dict[str, Any]:
    try:
        response = requests.get(API)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error: {e}")
    
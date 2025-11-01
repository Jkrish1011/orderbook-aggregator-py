import requests
from typing import Dict, Any

def get_coinbase_data(API) -> Dict[str, Any]:
    try:
        response = requests.get(API)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error: {e}")
    

def get_gemini_data(API) -> Dict[str, Any]:
    try:
        response = requests.get(API)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Error: {e}")
    
import os
from typing import Any, Dict

import requests


DEFAULT_BASE_URL = os.getenv("ECONAV_API_URL", "http://localhost:8000")


def fetch_eco_route(start: str, end: str, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    payload = {"start": start.strip().upper(), "end": end.strip().upper()}
    response = requests.post(f"{base_url}/api/v1/eco-route", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()

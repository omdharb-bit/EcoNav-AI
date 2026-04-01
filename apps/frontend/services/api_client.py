from __future__ import annotations

import os
from typing import Any

import requests

DEFAULT_BASE_URL = os.getenv("ECONAV_API_URL", "http://localhost:8000")


def fetch_eco_route(start: str, end: str, base_url: str | None = None) -> dict[str, Any]:
    url = (base_url or DEFAULT_BASE_URL).rstrip("/")
    payload = {"start": start.strip().upper(), "end": end.strip().upper()}
    response = requests.post(f"{url}/api/v1/eco-route", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()

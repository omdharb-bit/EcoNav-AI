"""Client for fetching real-time AQI data from the backend."""

from __future__ import annotations

from typing import Any

import requests

from apps.frontend.services.api_client import DEFAULT_BASE_URL


def fetch_all_aqi(base_url: str | None = None) -> dict[str, Any]:
    url = (base_url or DEFAULT_BASE_URL).rstrip("/")
    response = requests.get(f"{url}/api/v1/aqi", timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_city_aqi(city_code: str, base_url: str | None = None) -> dict[str, Any]:
    url = (base_url or DEFAULT_BASE_URL).rstrip("/")
    response = requests.get(f"{url}/api/v1/aqi/{city_code}", timeout=15)
    response.raise_for_status()
    return response.json()

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class RouteRequest(BaseModel):
    start: str
    end: str


class RouteResponse(BaseModel):
    route: List[str]
    total_distance: float
    total_pollution: float
    shortest_route: List[str]
    shortest_exposure: float
    improvement: str
    aqi_data: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    exposure_credits: Optional[Dict[str, Any]] = None
    shortest_credits: Optional[Dict[str, Any]] = None
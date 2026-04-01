from typing import List

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
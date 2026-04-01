from __future__ import annotations

from typing import List

from pydantic import BaseModel


class RouteAction(BaseModel):
    path: List[str]
    exposure: float


class RouteObservation(BaseModel):
    path: List[str]
    avg_aqi: int
    exposure: float
    score: float


class EnvState(BaseModel):
    current_location: str
    total_exposure: float

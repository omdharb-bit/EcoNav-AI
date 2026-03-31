from pydantic import BaseModel
from typing import List

# action sent by agent 
class RouteAction:
    def __init__(self, path, exposure):
        self.path = path
        self.exposure = exposure
    
# WHAT environment will return
class RouteObservation(BaseModel):
    path: List[str]
    avg_aqi: int
    exposure: float
    score: float
     
#Internal env. state 
class EnvState(BaseModel):
    current_location: str
    total_exposure: float 
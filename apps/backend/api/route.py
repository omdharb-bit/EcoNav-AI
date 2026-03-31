from fastapi import APIRouter
from apps.backend.services.eco_route_model import select_best_route
from apps.backend.services.eco_route_model import predict_score

router = APIRouter()

@router.post("/eco-route")
def eco_route(data: dict):
    routes = data.get("routes", [])

    for route in routes:
        route["score"] = predict_score(route)

    if not routes:
        return {"best_route": None, "all_routes": []}

    best = min(routes, key=lambda x: x["score"])

    return {
        "best_route": best,
        "all_routes": routes
    }


 
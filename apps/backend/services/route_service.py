"""Route service with real-time AQI integration.

Uses live air quality data (from Open-Meteo / WAQI) to compute edge
pollution weights instead of hardcoded values.  Falls back to default
weights when the AQI service is unreachable.
"""

from __future__ import annotations

from apps.backend.services.aqi_service import (
    fetch_all_cities_aqi,
    get_edge_pollution,
    get_pollution_weight_for_city,
)
from apps.backend.services.eco_route_model import choose_best_neighbor
from apps.simulator.evaluator import Graph, RLEnv, get_route
from packages.shared.utils import percent_improvement

# Default static distances (km) between cities — real distances along roads
EDGE_DISTANCES: dict[tuple[str, str], float] = {
    ("A", "B"): 280,   # Delhi → Jaipur
    ("A", "C"): 230,   # Delhi → Agra
    ("B", "D"): 680,   # Jaipur → Varanasi
    ("C", "D"): 540,   # Agra → Varanasi
    ("C", "E"): 330,   # Agra → Lucknow
    ("D", "E"): 300,   # Varanasi → Lucknow
    ("D", "F"): 680,   # Varanasi → Kolkata
    ("E", "F"): 990,   # Lucknow → Kolkata
}


# =====================
# HELPERS
# =====================
def compute_exposure(graph: Graph, path: list[str]) -> float:
    total = 0.0
    for i in range(len(path) - 1):
        for n, dist, pol in graph.get_neighbors(path[i]):
            if n == path[i + 1]:
                total += dist * pol
    return round(total, 2)


def compute_distance(graph: Graph, path: list[str]) -> float:
    total = 0.0
    for i in range(len(path) - 1):
        for n, dist, _ in graph.get_neighbors(path[i]):
            if n == path[i + 1]:
                total += dist
    return round(total, 2)


def _build_graph_with_real_aqi() -> tuple[Graph, dict]:
    """Build the city graph using real-time AQI-based pollution weights."""
    # Pre-fetch all cities' AQI in one shot (cached)
    all_aqi = fetch_all_cities_aqi()

    g = Graph()
    aqi_info: dict[str, dict] = {}

    for (c1, c2), dist in EDGE_DISTANCES.items():
        pollution = get_edge_pollution(c1, c2)
        g.add_road(c1, c2, dist, pollution)

    # Collect AQI summaries for the response
    for code, aqi_data in all_aqi.items():
        aqi_info[code] = {
            "city": aqi_data.city_name,
            "aqi": aqi_data.aqi,
            "category": aqi_data.category,
            "dominant_pollutant": aqi_data.dominant_pollutant,
            "pollution_weight": get_pollution_weight_for_city(code),
            "source": aqi_data.source,
        }

    return g, aqi_info


# =====================
# MAIN SERVICE
# =====================
def get_route_service(start: str, end: str):
    """Compute eco-route using real-time AQI pollution data."""

    g, aqi_info = _build_graph_with_real_aqi()

    # VALIDATION
    if start not in g.graph or end not in g.graph:
        return {"error": "Invalid start or end node"}

    # BASELINE ROUTE (shortest path)
    baseline = get_route(g, start, end)
    shortest_path = baseline["path"]
    shortest_exposure = baseline["total_exposure"]

    # RL ENV ROUTE (eco-optimised)
    env = RLEnv(g, start=start, destination=end)

    state = env.reset()
    path = [state]

    done = False
    visited = set()
    steps = 0

    while not done:
        visited.add(state)

        neighbors = g.get_neighbors(state)
        neighbors = [(n, d, p) for (n, d, p) in neighbors if n not in visited]

        if not neighbors:
            break

        action = choose_best_neighbor(
            type("obj", (), {"total_exposure": 0}),
            neighbors,
            destination=end,
        )

        next_state, reward, done = env.step(action)

        path.append(next_state)
        state = next_state

        steps += 1
        if steps > 20:
            break

    # FALLBACK
    if len(path) < 2 or path[-1] != end:
        eco_path = shortest_path
    else:
        eco_path = path

    # METRICS
    eco_exposure = compute_exposure(g, eco_path)
    eco_distance = compute_distance(g, eco_path)

    # IMPROVEMENT
    improvement_str = percent_improvement(shortest_exposure, eco_exposure)

    # EXPOSURE CREDITS
    from apps.backend.services.exposure_credit import (
        calculate_route_credits,
        route_credits_to_dict,
    )

    is_eco = eco_path != shortest_path
    eco_credits = calculate_route_credits(
        eco_path,
        distances=EDGE_DISTANCES,
        is_eco_route=is_eco,
        shortest_route=shortest_path,
    )
    shortest_credits = calculate_route_credits(
        shortest_path,
        distances=EDGE_DISTANCES,
        is_eco_route=False,
    )

    # RESPONSE
    return {
        "route": eco_path,
        "total_distance": eco_distance,
        "total_pollution": eco_exposure,
        "shortest_route": shortest_path,
        "shortest_exposure": shortest_exposure,
        "improvement": improvement_str,
        "aqi_data": aqi_info,
        "data_source": "real-time",
        "exposure_credits": route_credits_to_dict(eco_credits),
        "shortest_credits": route_credits_to_dict(shortest_credits),
    }
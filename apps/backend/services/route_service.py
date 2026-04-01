from apps.backend.services.eco_route_model import choose_best_neighbor
from apps.simulator.evaluator import Graph, RLEnv, get_route
from packages.shared.utils import percent_improvement


# =====================
# HELPERS
# =====================
def compute_exposure(graph, path):
    total = 0
    for i in range(len(path) - 1):
        for n, dist, pol in graph.get_neighbors(path[i]):
            if n == path[i + 1]:
                total += dist * pol
    return total


def compute_distance(graph, path):
    total = 0
    for i in range(len(path) - 1):
        for n, dist, _ in graph.get_neighbors(path[i]):
            if n == path[i + 1]:
                total += dist
    return total


# =====================
# MAIN SERVICE
# =====================
def get_route_service(start: str, end: str):

    # GRAPH SETUP
    g = Graph()

    g.add_road("A", "B", 5, 10)
    g.add_road("A", "C", 8, 3)
    g.add_road("B", "D", 2, 2)
    g.add_road("C", "D", 4, 6)
    g.add_road("C", "E", 7, 1)
    g.add_road("D", "E", 1, 2)
    g.add_road("D", "F", 6, 8)
    g.add_road("E", "F", 3, 1)

    # VALIDATION
    if start not in g.graph or end not in g.graph:
        return {"error": "Invalid start or end node"}

    # BASELINE ROUTE
    baseline = get_route(g, start, end)
    shortest_path = baseline["path"]
    shortest_exposure = baseline["total_exposure"]

    # RL ENV ROUTE
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
            destination=end
        )

        next_state, reward, done = env.step(action)

        path.append(next_state)
        state = next_state

        steps += 1
        if steps > 20:
            break

    # FALLBACK (CRITICAL)
    if len(path) < 2 or path[-1] != end:
        eco_path = shortest_path
    else:
        eco_path = path

    # METRICS
    eco_exposure = compute_exposure(g, eco_path)
    eco_distance = compute_distance(g, eco_path)

    # IMPROVEMENT
    improvement_str = percent_improvement(shortest_exposure, eco_exposure)

    # RESPONSE
    return {
        "route": eco_path,
        "total_distance": eco_distance,
        "total_pollution": eco_exposure,
        "shortest_route": shortest_path,
        "shortest_exposure": shortest_exposure,
        "improvement": improvement_str
    }
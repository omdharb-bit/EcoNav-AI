from fastapi import APIRouter
from apps.backend.services.eco_route_model import choose_best_neighbor
from apps.simulator.evaluator import Graph, RLEnv, get_route

router = APIRouter()


# =====================
# HELPER: EXPOSURE
# =====================
def compute_exposure(graph, path):
    total = 0
    for i in range(len(path) - 1):
        for n, dist, pol in graph.get_neighbors(path[i]):
            if n == path[i + 1]:
                total += dist * pol
    return total


@router.get("/eco-route")
def eco_route():

    # =====================
    # CREATE GRAPH
    # =====================
    g = Graph()

    g.add_road("A", "B", 5, 10)
    g.add_road("A", "C", 8, 3)
    g.add_road("B", "D", 2, 2)
    g.add_road("C", "D", 4, 6)
    g.add_road("C", "E", 7, 1)
    g.add_road("D", "E", 1, 2)
    g.add_road("D", "F", 6, 8)
    g.add_road("E", "F", 3, 1)

    # =====================
    # BASELINE (SHORTEST)
    # =====================
    baseline = get_route(g, "A", "F")

    shortest_path = baseline["path"]
    shortest_exposure = baseline["total_exposure"]

    # =====================
    # AI ENV ROUTE
    # =====================
    env = RLEnv(g, start="A", destination="F")

    state = env.reset()
    path = [state]

    done = False
    visited = set()
    steps = 0

    while not done:
        visited.add(state)

        neighbors = g.get_neighbors(state)

        # remove visited nodes
        neighbors = [(n, d, p) for (n, d, p) in neighbors if n not in visited]

        if not neighbors:
            break

        action = choose_best_neighbor(
            type("obj", (), {"total_exposure": 0}),
            neighbors,
            destination="F"
        )

        next_state, reward, done = env.step(action)

        path.append(next_state)
        state = next_state

        steps += 1
        if steps > 20:
            break

    eco_path = path

    # =====================
    # ECO EXPOSURE
    # =====================
    eco_exposure = compute_exposure(g, eco_path)

    # =====================
    # IMPROVEMENT
    # =====================
    if shortest_exposure > 0:
        improvement = (
            (shortest_exposure - eco_exposure) / shortest_exposure * 100
        )
        improvement_str = f"{improvement:.2f}% less pollution"
    else:
        improvement_str = "N/A"

    # =====================
    # FINAL RESPONSE
    # =====================
    return {
        "eco_route": eco_path,
        "shortest_route": shortest_path,
        "eco_exposure": eco_exposure,
        "shortest_exposure": shortest_exposure,
        "improvement": improvement_str
    }
import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
MODEL_PATH = os.path.join(BASE_DIR, "models", "eco_model.json")

DEFAULT_WEIGHTS = {
    "distance_weight": 0.15,
    "pollution_weight": 0.45,
    "exposure_weight": 0.4,
}

_weights = DEFAULT_WEIGHTS.copy()


def _load_weights() -> bool:
    global _weights
    if not os.path.exists(MODEL_PATH):
        _weights = DEFAULT_WEIGHTS.copy()
        return False

    with open(MODEL_PATH, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    _weights = {
        "distance_weight": float(
            data.get("distance_weight", DEFAULT_WEIGHTS["distance_weight"])
        ),
        "pollution_weight": float(
            data.get("pollution_weight", DEFAULT_WEIGHTS["pollution_weight"])
        ),
        "exposure_weight": float(
            data.get("exposure_weight", DEFAULT_WEIGHTS["exposure_weight"])
        ),
    }
    return True


_load_weights()


def reload_model():
    if _load_weights():
        print("[OK] Model weights hot-reloaded successfully!")
    else:
        print(f"[WARN] Model file not found at: {MODEL_PATH}. Using defaults.")


def predict_score_from_env(state, node, distance, pollution):
    _ = node
    return (
        distance * _weights["distance_weight"]
        + pollution * _weights["pollution_weight"]
        + state.total_exposure * _weights["exposure_weight"]
    )


def choose_best_neighbor(state, neighbors, destination):
    if not neighbors:
        raise ValueError("No neighbors available for decision")

    best_node = None
    best_score = float("inf")

    for node, distance, pollution in neighbors:
        model_score = predict_score_from_env(state, node, distance, pollution)
        goal_bonus = -10 if node == destination else 0
        final_score = model_score + goal_bonus

        if final_score < best_score:
            best_score = final_score
            best_node = node

    return best_node if best_node is not None else min(neighbors, key=lambda x: x[2])[0]

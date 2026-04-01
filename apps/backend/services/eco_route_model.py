import torch
import torch.nn as nn
import os

# =========================================================
# MODEL DEFINITION (MUST MATCH TRAINING EXACTLY)
# =========================================================
class EcoModel(nn.Module):
    def __init__(self):
        super(EcoModel, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x):
        return self.net(x)


# =========================================================
# PATH SETUP (FIXED)
# =========================================================
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

MODEL_PATH = os.path.join(BASE_DIR, "models", "eco_model.pth")


# =========================================================
# LOAD MODEL (SAFE + CORRECT)
# =========================================================
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

model = EcoModel()

try:
    model.load_state_dict(
        torch.load(MODEL_PATH, map_location=torch.device("cpu"))
    )
    model.eval()
    print(f"[OK] EcoModel loaded from: {MODEL_PATH}")
except Exception as e:
    raise RuntimeError(f"Model loading failed: {e}")


# =========================================================
# HOT RELOAD (OPTIONAL BUT VERY USEFUL)
# =========================================================
def reload_model():
    global model
    try:
        new_model = EcoModel()
        new_model.load_state_dict(
            torch.load(MODEL_PATH, map_location=torch.device("cpu"))
        )
        new_model.eval()
        model = new_model
        print("[OK] Model hot-reloaded successfully!")
    except Exception as e:
        print(f"[ERROR] Reload failed: {e}")


# =========================================================
# FEATURE ADAPTER (ENV → MODEL INPUT)
# =========================================================
def predict_score_from_env(state, node, distance, pollution):
    try:
        features = [
            distance / 100.0,
            pollution / 100.0,
            state.total_exposure / 100.0
        ]

        x = torch.tensor([features], dtype=torch.float32)

        with torch.no_grad():
            prediction = model(x)

        return float(prediction.item())

    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        return float("inf")


# =========================================================
# DECISION ENGINE (CORE AI LOGIC)
# =========================================================
def choose_best_neighbor(state, neighbors, destination):

    if not neighbors:
        raise ValueError("No neighbors available for decision")

    best_node = None
    best_score = float("inf")

    for node, distance, pollution in neighbors:

        model_score = predict_score_from_env(
            state,
            node,
            distance,
            pollution
        )

        # 🎯 destination awareness
        goal_bonus = -10 if node == destination else 0

        final_score = (
            model_score
            + 0.3 * (distance / 100.0)
            + 0.7 * (pollution / 100.0)
            + goal_bonus
        )

        print(
            f"[AI] node={node} | dist={distance} | poll={pollution} "
            f"| model={model_score:.4f} | final={final_score:.4f}"
        )

        if final_score < best_score:
            best_score = final_score
            best_node = node

    if best_node is None:
        print("[WARN] Model failed, using fallback (min pollution)")
        best_node = min(neighbors, key=lambda x: x[2])[0]

    return best_node
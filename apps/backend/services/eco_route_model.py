import torch
import torch.nn as nn

# ---- Model Definition (same as training) ----
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

# ---- Load model ----
model = EcoModel()
model.load_state_dict(torch.load("models/eco_model.pth"))
model.eval()

def reload_model():
    global model
    try:
        new_model = EcoModel()
        new_model.load_state_dict(torch.load("models/eco_model.pth"))
        new_model.eval()
        model = new_model
        print("[OK] Active model weights hot-reloaded successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to reload model: {e}")

# ---- Prediction function ----
def predict_score(route):
    # ⚠️ Adjust these keys based on your data
    features = [
        route.get("distance", 0),
        route.get("traffic", 0),
        route.get("fuel", 0)
    ]

    x = torch.tensor([features], dtype=torch.float32)

    with torch.no_grad():
        prediction = model(x)

    return float(prediction.item())


# ---- Optional (if used somewhere else) ----
def select_best_route(routes):
    return min(routes, key=lambda x: x["score"])
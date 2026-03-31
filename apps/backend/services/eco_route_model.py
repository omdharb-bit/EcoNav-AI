import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

model = None
model_last_modified = 0

def get_model():
    global model, model_last_modified
    model_path = "models/eco_model.pkl"
    
    if not os.path.exists(model_path):
        return None
        
    current_mtime = os.path.getmtime(model_path)
    
    if model is None or current_mtime > model_last_modified:
        print(f"Reloading ML model... (modified: {current_mtime})")
        model = joblib.load(model_path)
        model_last_modified = current_mtime
        
    return model

def predict_score(route: dict):
    m = get_model()
    if m is None:
        return 999.0 # Fallback penalty if model missing

    # Model expects 3 features: [distance, traffic, pollution]
    features = np.array([[
        route.get("distance", 0),
        route.get("traffic", 0),
        route.get("pollution", 0)
    ]])
    return float(m.predict(features)[0])
# -------------------------------
# CO2 EMISSION CALCULATION
# -------------------------------
def calculate_co2(distance_km, vehicle_type="car"):
    emission_factors = {
        "car": 120,
        "bike": 80,
        "bus": 60,
        "walk": 0
    }
    return distance_km * emission_factors.get(vehicle_type, 100)


# -------------------------------
# ECO SCORE FUNCTION
# -------------------------------
def eco_score(distance, traffic, pollution):
    """
    Lower score = better route
    """
    return (
        0.5 * distance +
        0.3 * traffic +
        0.2 * pollution
    )


# -------------------------------
# BEST ROUTE Selector
# -------------------------------
def select_best_route(routes, vehicle_type="car"):
    """
    routes = [
        {
            "id": 1,
            "distance": 10,
            "traffic": 7,
            "pollution": 5
        }
    ]
    """

    best_route = None
    best_score = float("inf")

    for route in routes:
        co2 = calculate_co2(route["distance"], vehicle_type)
        score = eco_score(
            route["distance"],
            route["traffic"],
            route["pollution"]
        )

        route["eco_score"] = score
        route["co2"] = co2

        if score < best_score:
            best_score = score
            best_route = route

    return {
        "best_route": best_route,
        "all_routes": routes
    }

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

MODEL_PATH = "models/eco_model.pkl"
DATA_PATH = "data/training_data.csv"

def run_training_pipeline():
    print("Starting automated model training...")
    if not os.path.exists(DATA_PATH):
        print(f"No training data found at {DATA_PATH}. Skipping training.")
        return False
        
    df = pd.read_csv(DATA_PATH)
    
    # Assuming CSV structure is: distance, traffic, pollution, eco_score
    X = df[['distance', 'traffic', 'pollution']].values
    y = df['eco_score'].values
    
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model successfully trained on {len(df)} samples and saved to {MODEL_PATH}")
    return True

if __name__ == "__main__":
    run_training_pipeline()
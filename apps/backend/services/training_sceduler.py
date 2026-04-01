import time
import threading
import subprocess

def train_model():
    while True:
        print("[Update] Starting automated training...")

        try:
            subprocess.run(["python", "models/train_model.py"], check=True)
            print("[OK] Training completed!")
            
            # Hot-reload the weights in the FastApi application
            from apps.backend.services.eco_route_model import reload_model
            reload_model()
        except Exception as e:
            print("[ERROR] Training failed:", e)

        print("Waiting 10 minutes (600 seconds) until next automated training run...")
        time.sleep(600)


def start_training_scheduler():
    thread = threading.Thread(target=train_model, daemon=True)
    thread.start()
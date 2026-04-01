import time
import threading
import subprocess
import datetime

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

        # Calculate exact next run time
        next_run = datetime.datetime.now() + datetime.timedelta(seconds=600)
        print(f"Waiting 10 minutes. Next automated training scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(600)


def start_training_scheduler():
    thread = threading.Thread(target=train_model, daemon=True)
    thread.start()
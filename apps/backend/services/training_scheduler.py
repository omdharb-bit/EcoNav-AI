import asyncio
from models.train_model import run_training_pipeline

class TrainingScheduler:
    def __init__(self, interval_seconds: int = 3600 * 24): # 24 hours by default
        self.interval_seconds = interval_seconds
        self.is_running = False
        self._task = None

    async def start(self):
        """Starts the background training loop."""
        self.is_running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        """Stops the background training loop."""
        self.is_running = False
        if self._task:
            self._task.cancel()

    async def _run(self):
        """The actual scheduler loop."""
        print("Model training scheduler started!")
        while self.is_running:
            try:
                # We use asyncio.to_thread to run the sync ML blocking code
                # so it doesn't freeze the FastAPI asynchronous event loop
                success = await asyncio.to_thread(run_training_pipeline)
                if success:
                    import datetime
                    next_run = datetime.datetime.now() + datetime.timedelta(seconds=self.interval_seconds)
                    print(f"Automated training completed successfully. Next run scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print("Automated training skipped.")
            except Exception as e:
                print(f"Error during automated training: {e}")
            
            await asyncio.sleep(self.interval_seconds)
            
# A singleton instance you can import into main.py
scheduler = TrainingScheduler(interval_seconds=600)  # Set to 10 minutes for testing purposes

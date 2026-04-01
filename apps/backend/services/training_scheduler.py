import asyncio
import datetime

from models.train_model import run_training_pipeline


class TrainingScheduler:
    def __init__(self, interval_seconds: int = 3600 * 24):
        self.interval_seconds = interval_seconds
        self.is_running = False
        self._task = None

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self):
        print("Model training scheduler started!")
        while self.is_running:
            try:
                success = await asyncio.to_thread(run_training_pipeline)
                if success:
                    next_run = datetime.datetime.now() + datetime.timedelta(
                        seconds=self.interval_seconds
                    )
                    print(
                        "Automated training completed successfully. "
                        f"Next run scheduled at: {next_run:%Y-%m-%d %H:%M:%S}"
                    )
                else:
                    print("Automated training skipped.")
            except Exception as exc:
                print(f"Error during automated training: {exc}")

            await asyncio.sleep(self.interval_seconds)


scheduler = TrainingScheduler(interval_seconds=600)

from fastapi import FastAPI
from contextlib import asynccontextmanager
from apps.backend.services.ai_model import choose_best_route
from apps.backend.api.route import router as eco_router
from apps.backend.services.training_scheduler import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the automated training scheduler loop
    await scheduler.start()
    yield
    # Shutdown: Stop the training task gracefully
    await scheduler.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(eco_router, prefix="/api/v1")


@app.get("/")
def home():
    return {"message": "EcoNav AI Running 🚀"}


@app.get("/route")
def get_best_route():
    # sample routes (later can come from maps API)
    routes = [
        {"path": ["A", "B", "C"], "distance": 5, "traffic": 3},
        {"path": ["A", "D", "C"], "distance": 6, "traffic": 2},
        {"path": ["A", "E", "C"], "distance": 4, "traffic": 6},
    ]

    best, all_routes = choose_best_route(routes)

    return {"best_route": best, "all_routes": all_routes}

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from apps.backend.api.aqi import router as aqi_router
from apps.backend.api.credits import router as credits_router
from apps.backend.api.graph import router as graph_router
from apps.backend.api.network import router as network_router
from apps.backend.api.route import router as eco_router
from apps.backend.api.simulate import router as simulate_router
from apps.backend.api.training import router as training_router
from apps.backend.core.config import settings
from apps.backend.services.ai_model import choose_best_route
from apps.backend.services.aqi_service import fetch_route_cities_aqi
from apps.backend.services.training_scheduler import scheduler
from packages.env_core.core.api import router as openenv_router

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Pre-fetch only route cities (6) for fast startup; full 50+ loaded on demand
    await asyncio.to_thread(fetch_route_cities_aqi)
    await scheduler.start()
    yield
    await scheduler.stop()


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(eco_router, prefix="/api/v1")
app.include_router(training_router, prefix="/api/v1/train")
app.include_router(graph_router, prefix="/api/v1/graph")
app.include_router(aqi_router, prefix="/api/v1")
app.include_router(credits_router, prefix="/api/v1")
app.include_router(network_router, prefix="/api/v1")
app.include_router(simulate_router, prefix="/api/v1")

# OpenEnv standard endpoints at root level for spec compliance
app.include_router(openenv_router)


@app.get("/route")
def get_best_route():
    routes = [
        {"path": ["A", "B", "C"], "distance": 5, "traffic": 3},
        {"path": ["A", "D", "C"], "distance": 6, "traffic": 2},
        {"path": ["A", "E", "C"], "distance": 4, "traffic": 6},
    ]
    best, all_routes = choose_best_route(routes)
    return {"best_route": best, "all_routes": all_routes}


# Serve frontend at root - mount this LAST to avoid stealing API routes
frontend_path = os.path.abspath("apps/frontend")
public_path = os.path.join(frontend_path, "public")

# Mount public assets first so they are available at the root URL
if os.path.exists(public_path):
    app.mount("/", StaticFiles(directory=public_path), name="public")

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.backend.api.aqi import router as aqi_router
from apps.backend.api.credits import router as credits_router
from apps.backend.api.route import router as eco_router
from packages.env_core.core.api import router as openenv_router
from apps.backend.core.config import settings
from apps.backend.services.ai_model import choose_best_route
from apps.backend.services.aqi_service import fetch_route_cities_aqi
from apps.backend.services.training_scheduler import scheduler

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
app.include_router(aqi_router, prefix="/api/v1")
app.include_router(credits_router, prefix="/api/v1")

# OpenEnv standard endpoints at root level for spec compliance
app.include_router(openenv_router)


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="apps/frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("apps/frontend/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.VERSION}


@app.get("/route")
def get_best_route():
    routes = [
        {"path": ["A", "B", "C"], "distance": 5, "traffic": 3},
        {"path": ["A", "D", "C"], "distance": 6, "traffic": 2},
        {"path": ["A", "E", "C"], "distance": 4, "traffic": 6},
    ]

    best, all_routes = choose_best_route(routes)

    return {"best_route": best, "all_routes": all_routes}

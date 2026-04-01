# 🌱 EcoNav AI

AI-powered environmental routing system that recommends lower-exposure routes instead of only fastest routes.

## Project Modules

- `apps/backend` — FastAPI service exposing eco-route APIs.
- `apps/frontend` — Streamlit UI for route exploration.
- `apps/simulator` — route simulator and fuel-model trainer.
- `models` — training pipeline and persisted model artifacts.
- `infra/docker` — production-ready Dockerfiles and compose stack.
- `infra/ci/github-actions.yml` — CI/CD pipeline for lint, tests, and image builds.

## Quickstart (Local)

```bash
bash infra/scripts/setup.sh
python scripts/seed_data.py
python models/train_model.py
pytest
uvicorn apps.backend.main:app --reload
```

In another terminal:

```bash
streamlit run apps/frontend/app.py
```

## One-command local run

```bash
bash infra/scripts/run_all.sh
```

## Docker run

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`

## API Endpoints

- `GET /health` — service health/version.
- `POST /api/v1/eco-route` — compute eco route using start/end nodes.
- `GET /route` — demo endpoint for route ranking.

## CI/CD

GitHub Actions pipeline includes:

1. Dependency install
2. Data seeding
3. Ruff lint
4. Pytest test suite
5. Smoke test script
6. Docker image builds for backend/frontend

## Hackathon Demo Checklist

- [x] Frontend + backend connected
- [x] Training artifact generated (`models/eco_model.json`)
- [x] Automated retraining scheduler in API lifespan
- [x] CI pipeline for quality gates
- [x] Dockerized deployment stack

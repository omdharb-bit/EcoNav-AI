---
title: EcoNav AI
emoji: 🌍
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: true
---

# 🌱 EcoNav AI — Exposure Credit Platform

[![EcoNav CI/CD](https://github.com/omdharb-bit/EcoNav-AI/actions/workflows/main.yml/badge.svg)](https://github.com/omdharb-bit/EcoNav-AI/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenEnv Compliant](https://img.shields.io/badge/OpenEnv-Compliant-10b981)](https://github.com/OpenEnv/spec)

EcoNav AI is an **intelligent routing platform** and Reinforcement Learning (RL) environment built for the **Meta AI Environmental Decision Intelligence Hackathon**. It empowers users and agents to navigate urban networks while minimizing pollution exposure and maximizing health "Exposure Credits."

---

## 🌍 Project Overview

EcoNav AI transforms navigation from a simple distance-minimization problem into a **multi-objective environmental optimization task**. By integrating real-time Air Quality Index (AQI) data with dynamic traffic simulations, the platform provides a realistic testing ground for eco-aware agents.

### Key Innovations:
- **Live AQI Integration**: Real-time pollution data fetched from the Open-Meteo API for 50+ network nodes across India.
- **Exposure Credits**: A gamified health currency that penalizes high-pollution segments (Grade F) and rewards clean-air segments (Grade A).
- **Dynamic Traffic Engine**: Simulates congestion levels that impact both travel time and localized pollution exposure.
- **OpenEnv Compliance**: Fully compatible with the OpenEnv specification for RL evaluation and agent deployment.

---

## 🛠 Tech Stack

The project is architected as a modern **monorepo** for seamless development and deployment.

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic, Torch (ML scoring).
- **Frontend**: Vite, Vanilla JS, CSS3 (Glassmorphism), Leaflet.js (Mapping), Chart.js (Analytics).
- **Infrastructure**: Docker, Turbo (Build system), GitHub Actions (CI/CD).
- **Quality**: Ruff (Linting), Prettier (Formatting).

---

## 📂 Repository Structure

```text
EcoNav-AI/
├── apps/
│   ├── backend/         # FastAPI server, AI services, and RL endpoints
│   ├── frontend/        # Vite-powered dashboard and mapping interface
│   ├── simulator/       # ML training and evaluation logic
│   └── web/             # (Deprecated) Static web assets
├── packages/
│   └── env_core/        # Shared RL environment logic (OpenEnv Spec)
├── requirements/        # Modularized dependency lists
├── server/              # Production entry points for Docker/HF Spaces
├── turbo.json           # Monorepo configuration
└── inference.py         # Baseline agent evaluation script
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: >= 18.0.0
- **Python**: >= 3.10
- **npm**: >= 11.11.0

### Quick Start (Recommended)
1. **Clone the repository**:
   ```bash
   git clone https://github.com/omdharb-bit/EcoNav-AI.git
   cd EcoNav-AI
   ```

2. **Install Dependencies**:
   ```bash
   npm install      # Installs monorepo build tools
   pip install -r requirements/backend.txt  # Installs Python backend deps
   ```

3. **Run Everything**:
   Use the Turbo-powered development command to start both the backend and frontend:
   ```bash
   npm run dev
   ```
   *Note: If running on Windows, you may need to set `PYTHONPATH="."` manually if starting the backend via script.*

### Manual Startup
- **Backend**: `python server/app.py` (Runs on [http://localhost:7860](http://localhost:7860))
- **Frontend**: `npm run dev --prefix apps/frontend` (Runs on [http://localhost:5173](http://localhost:5173))

---

## 🧠 RL Evaluation (OpenEnv)

The environment supports four standard evaluation tasks of increasing complexity:
1. `easy_route`: Delhi to Kolkata (15 steps).
2. `medium_route`: Delhi to Kolkata (8 steps).
3. `hard_pollution_dodge`: Agra to Kolkata (6 steps).
4. `expert_credit_max`: Maximize credits while reaching the goal (10 steps).

**Baseline Evaluation**:
```bash
export ENV_URL="http://127.0.0.1:7860"
python inference.py
```

---

## 🧪 Development & Quality

We maintain high code quality standards through automated linting and formatting.

- **Linting (Python)**: `ruff check .`
- **Fix Linting**: `ruff check --fix .`
- **Formatting (JS/TS/MD)**: `npm run format`

---

## 🏆 Project Status

| Check | Status |
|---|---|
| **CI/CD Pipeline** | Passing ✅ |
| **OpenEnv Spec** | Compliant (v1.0) 🟢 |
| **Real-time Data** | Active (Open-Meteo) 🛰️ |
| **Model Version** | EcoScorer v2.1 🧠 |

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.


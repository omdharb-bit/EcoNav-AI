# 🌱 EcoNav AI — Exposure Credit OpenEnv

An OpenEnv-compliant Reinforcement Learning environment built for the Meta AI Environmental Decision Intelligence Hackathon. 

## 🌍 Environment Description & Motivation

EcoNav AI models a realistic urban navigation challenge where an intelligent agent must route through an Indian city network (represented as a dynamic graph). Instead of optimizing solely for distance or time, the agent optimizes to **minimize pollution exposure** and maximize **Exposure Credits**—a gamified health currency.

What makes this environment highly functional and unique is its integration with **live, real-world data**. The environment fetches real-time Air Quality Index (AQI) values from the Open-Meteo API. As the agent navigates segments, edge weights (pollution levels) dynamically shift based on reality. The agent earns credits for traversing clean-air segments (Grade A) and loses credits for heavily polluted segments (Grade F). This fills a real gap in mobility algorithms: exposure-aware routing evaluated as an RL task.

## 🧠 Action and Observation Spaces

### Observation Space
The observation space is a strictly typed JSON dictionary detailing the agent's current location, remaining budget, and available next moves including real-time sensor metrics:
- `current_city` (str): Current city code (e.g. "A").
- `current_city_name` (str): Human readable city name (e.g. "Delhi").
- `destination` (str): Target destination code.
- `destination_name` (str): Target human readable city name.
- `visited` (list[str]): City codes already traversed.
- `neighbors` (list[dict]): Available adjacent cities, featuring:
  - `distance`: Distance to neighbor (km).
  - `aqi`: Real-time Air Quality Index.
  - `grade`: Computed health grade (A to F).
  - `credit_delta`: Credits that will be won or lost by making this move.
- `exposure_credits` (int): Current credit balance (starts at 100).
- `total_exposure` (float): Cumulative normalized pollution exposure metric.
- `steps_taken` (int): Number of steps used in current episode.
- `max_steps` (int): Step budget limit for the current task.

### Action Space
- `city` (str): A string specifying the city code to move to next. The chosen code must belong to the list of current `neighbors`.

## 📜 Tasks & Expected Difficulty

Four discrete tasks of increasing difficulty force the agent to balance trade-offs between step budget, distance, and real-world pollution grids.

1. **`easy_route` (Easy)**: Navigate from highly-polluted Delhi to Kolkata. Generous step budget (15 steps) allowing maximum flexibility to seek clean air routes. Baseline passing score: 0.5.
2. **`medium_route` (Medium)**: Same route, but optimized budget (8 steps). Requires balancing direct paths with pollution spikes. Baseline passing score: 0.6.
3. **`hard_pollution_dodge` (Hard)**: Start from Agra to Kolkata with a tight budget (6 steps). Requires aggressive credit optimization to survive the early exposure hits of Northern India. Baseline passing score: 0.7.
4. **`expert_credit_max` (Expert)**: Maximize exposure credits while reaching Kolkata within 10 steps. A rigorous test of the agent's multi-objective reward policy. Baseline passing score: 0.8.

## 🏆 Baseline Scores

We ran the included `inference.py` evaluating a greedy baseline heuristic (which strictly prefers neighbors with higher credit deltas and lower AQI values).

| Task | Score (0.0 - 1.0) | Grade | Credits Final | Reached Goal |
|---|---|---|---|---|
| `easy_route` | 0.8161 | B | 110 | ✅ |
| `medium_route` | 0.8161 | B | 110 | ✅ |
| `hard_pollution_dodge` | 0.8326 | B | 105 | ✅ |
| `expert_credit_max`| 0.8161 | B | 110 | ✅ |
| **Average Score** | **0.8202** | | | |

## 🚀 Setup and Usage Instructions

### Run via Docker (Hugging Face Spaces)
The provided `Dockerfile` is optimized to run on Hugging Face Spaces per the OpenEnv specification (automatically exposing port `7860`).
```bash
docker build -t econav-openenv .
docker run -p 7860:7860 econav-openenv
```

### Local Development Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt # OR pip install fastapi uvicorn requests pydantic openai numpy pyyaml

# Start the environment
uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000
```

### Running Inference
Run the baseline evaluation or LLM-driven agent via `inference.py`.

**To run the greedy baseline:**
```bash
export ENV_URL="http://127.0.0.1:8000"
python inference.py
```

**To run the LLM Agent (OpenAI Client format):**
```bash
export ENV_URL="http://127.0.0.1:8000"
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export HF_TOKEN="your-hf-token"

python inference.py
```

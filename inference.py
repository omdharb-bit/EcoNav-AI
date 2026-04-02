"""
Inference Script Example
================================

MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.

- The inference script must be named 'inference.py' and placed in the root directory of the project
- Participants must use OpenAI Client for all LLM calls using above variables
"""

import os
import json
import requests
from typing import Any

# ---------------------------------------------------------------------------
# Environment config
# ---------------------------------------------------------------------------

ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")

MAX_STEPS = 15


# ---------------------------------------------------------------------------
# Environment interaction helpers
# ---------------------------------------------------------------------------

def env_reset(task_id: str = "easy_route") -> dict:
    """Call /reset endpoint."""
    resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def env_step(city: str) -> dict:
    """Call /step endpoint with an action."""
    resp = requests.post(
        f"{ENV_URL}/step",
        json={"action": {"city": city}},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def env_state() -> dict:
    """Call /state endpoint."""
    resp = requests.get(f"{ENV_URL}/state", timeout=10)
    resp.raise_for_status()
    return resp.json()


def env_grade() -> dict:
    """Call /grade endpoint."""
    resp = requests.get(f"{ENV_URL}/grade", timeout=10)
    resp.raise_for_status()
    return resp.json()


def env_tasks() -> list[dict]:
    """Get available tasks."""
    resp = requests.get(f"{ENV_URL}/tasks", timeout=10)
    resp.raise_for_status()
    return resp.json()["tasks"]


# ---------------------------------------------------------------------------
# LLM-based agent (uses OpenAI client)
# ---------------------------------------------------------------------------

def get_llm_action(observation: dict) -> str:
    """Ask the LLM to choose the next city based on observation."""
    from openai import OpenAI

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    neighbors = observation.get("neighbors", [])
    neighbor_text = "\n".join(
        f"  - {n['city']} ({n['city_name']}): AQI={n['aqi']}, Grade={n['grade']}, "
        f"Credits={n['credit_delta']:+d}, Distance={n['distance']}km"
        for n in neighbors
    )

    prompt = f"""You are an AI navigation agent in the EcoNav environment.
Your goal: reach {observation['destination']} ({observation['destination_name']}) while maximizing exposure credits.

Current state:
- Location: {observation['current_city']} ({observation['current_city_name']})
- Destination: {observation['destination']} ({observation['destination_name']})
- Credits: {observation['exposure_credits']}
- Steps: {observation['steps_taken']}/{observation['max_steps']}
- Visited: {observation['visited']}
- Total exposure: {observation['total_exposure']}

Available moves:
{neighbor_text}

Rules:
- Choose cities with lower AQI (Grade A/B) to EARN credits
- Avoid high-AQI cities (Grade D/E/F) that LOSE credits
- You MUST reach the destination before running out of steps
- Balance: short path vs clean-air path

Reply with ONLY the city code (e.g., "E") — nothing else."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.2,
        )
        action = response.choices[0].message.content.strip().upper()
        # Validate it's a real neighbor
        valid = [n["city"] for n in neighbors]
        if action in valid:
            return action
        # Try to extract a valid city code from the response
        for v in valid:
            if v in action:
                return v
        # Fallback to greedy
        return greedy_action(observation)
    except Exception as e:
        print(f"LLM error: {e}, falling back to greedy")
        return greedy_action(observation)


# ---------------------------------------------------------------------------
# Greedy baseline agent (no LLM needed)
# ---------------------------------------------------------------------------

def greedy_action(observation: dict) -> str:
    """Simple greedy agent: prefer neighbors closer to destination with better AQI."""
    neighbors = observation.get("neighbors", [])
    destination = observation["destination"]
    visited = set(observation.get("visited", []))

    if not neighbors:
        raise ValueError("No neighbors available!")

    # Priority: destination if available
    for n in neighbors:
        if n["city"] == destination:
            return n["city"]

    # Filter unvisited
    unvisited = [n for n in neighbors if n["city"] not in visited]
    candidates = unvisited if unvisited else neighbors

    # Score: higher credit_delta is better, lower AQI is better
    best = max(candidates, key=lambda n: n["credit_delta"] * 2 - n["aqi"] / 50)
    return best["city"]


# ---------------------------------------------------------------------------
# Main inference loop
# ---------------------------------------------------------------------------

def run_episode(task_id: str = "easy_route", use_llm: bool = False) -> dict:
    """Run a complete episode on the given task."""
    print(f"\n{'='*60}")
    print(f"Task: {task_id}")
    print(f"Agent: {'LLM' if use_llm else 'Greedy Baseline'}")
    print(f"{'='*60}")

    obs = env_reset(task_id)
    print(f"Start: {obs['current_city']} ({obs['current_city_name']})")
    print(f"Goal:  {obs['destination']} ({obs['destination_name']})")
    print(f"Credits: {obs['exposure_credits']}, Max steps: {obs['max_steps']}")

    total_reward = 0.0

    while not obs.get("done", False):
        # Choose action
        if use_llm:
            action = get_llm_action(obs)
        else:
            action = greedy_action(obs)

        print(f"\n  Step {obs['steps_taken']+1}: Moving to {action}...")

        # Execute
        result = env_step(action)
        obs = result["observation"]
        reward = result["reward"]
        total_reward += reward
        info = result["info"]

        print(f"    → {obs['current_city']} ({obs['current_city_name']})")
        print(f"    Grade: {info['segment_grade']}, AQI: {info['segment_avg_aqi']}")
        print(f"    Credits: {info['segment_credit_delta']:+d} → Balance: {obs['exposure_credits']}")
        print(f"    Reward: {reward:.2f}")

    # Grade
    grade = env_grade()
    print(f"\n{'─'*60}")
    print(f"RESULT: {grade['grade_letter']} (Score: {grade['score']:.4f})")
    print(f"Route: {' → '.join(grade['route'])}")
    print(f"Credits: {grade['exposure_credits_final']} | Exposure: {grade['total_exposure']}")
    print(f"Feedback: {grade['feedback']}")
    print(f"Total reward: {total_reward:.2f}")

    return grade


def main():
    """Run baseline inference on all tasks."""
    tasks = env_tasks()
    print(f"Available tasks: {[t['id'] for t in tasks]}")

    results = []
    for task in tasks:
        use_llm = bool(API_KEY)  # Use LLM if API key is set
        grade = run_episode(task["id"], use_llm=use_llm)
        results.append({
            "task": task["id"],
            "difficulty": task["difficulty"],
            "score": grade["score"],
            "grade": grade["grade_letter"],
            "reached": grade["reached_destination"],
            "credits": grade["exposure_credits_final"],
        })

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "✅" if r["reached"] else "❌"
        print(f"  {status} {r['task']:25s} Score={r['score']:.4f}  Grade={r['grade']}  Credits={r['credits']}")

    avg_score = sum(r["score"] for r in results) / len(results)
    print(f"\n  Average score: {avg_score:.4f}")

    return results


if __name__ == "__main__":
    main()

import sys
import os
import random

# Fix path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(BASE_DIR)

from packages.env_core.envs.pollution_env.env import PollutionEnv
from apps.simulator.evaluator import Graph


# ===================== TEST GRAPH =====================

def test_graph():
    print("\n🧪 TESTING GRAPH\n")

    g = Graph()
    g.add_road("A", "B", 5, 10)
    g.add_road("A", "C", 8, 3)

    print("Neighbors of A:", g.get_neighbors("A"))


# ===================== TEST RL ENV =====================

def test_rl_env():
    print("\n🚀 TESTING RL ENV\n")

    g = Graph()

    g.add_road("A", "B", 5, 10)
    g.add_road("A", "C", 8, 3)
    g.add_road("B", "D", 2, 2)
    g.add_road("C", "D", 4, 6)
    g.add_road("C", "E", 7, 1)
    g.add_road("D", "E", 1, 2)
    g.add_road("D", "F", 6, 8)
    g.add_road("E", "F", 3, 1)

    env = PollutionEnv(g, start="A", destination="F")

    state = env.reset()
    print("Start:", state)

    done = False

    while not done:
        actions = env.get_possible_actions()

        action = random.choice(actions)

        next_state, reward, done, info = env.step(action)

        print(f"{state} → {action} | reward={reward}")

        state = next_state

    print("\n✅ FINAL RESULT")
    print("Total Exposure:", info["total_exposure"])


# ===================== RUN =====================

if __name__ == "__main__":
    test_graph()
    test_rl_env()
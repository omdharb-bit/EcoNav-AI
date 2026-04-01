from __future__ import annotations

import random
from collections import defaultdict


class RLAgent:
    def __init__(self, epsilon: float = 0.2) -> None:
        self.epsilon = epsilon
        self.q = defaultdict(lambda: defaultdict(float))

    def choose_action(self, state: str, actions: list[str]) -> str:
        if not actions:
            raise ValueError("No actions available")
        if random.random() < self.epsilon:
            return random.choice(actions)
        return max(actions, key=lambda action: self.q[state][action])

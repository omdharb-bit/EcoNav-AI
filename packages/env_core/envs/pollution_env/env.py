def step(self, action: str):
    neighbors = self.graph.get_neighbors(self.current_location)

    edge = None
    for n, dist, pol in neighbors:
        if n == action:
            edge = (n, dist, pol)
            break

    if edge is None:
        raise ValueError(f"Invalid action: {action}")

    next_node, distance, pollution = edge

    # 📊 Exposure tracking (IMPORTANT)
    exposure = distance * pollution
    self.total_exposure += exposure

    self.current_location = next_node
    self.steps_taken += 1

    # 🎯 Balanced reward
    reward = -(pollution * 0.7 + distance * 0.3)

    # 🌿 Controlled green bonus
    reward += 0.5 * max(0, 10 - pollution)

    # 📍 Optional heuristic guidance
    if hasattr(self.graph, "heuristic"):
        reward -= 0.1 * self.graph.heuristic(next_node, self.destination)

    done = next_node == self.destination

    if done:
        reward += 100

    if self.steps_taken >= self.max_steps:
        reward -= 50
        done = True

    return next_node, reward, done
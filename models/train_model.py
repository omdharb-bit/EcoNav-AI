import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# ---- Sample Data (replace with your real data) ----
# Example: 3 features → 1 output
X = np.array([
    [1, 2, 3],
    [2, 3, 4],
    [3, 4, 5]
], dtype=np.float32)

y = np.array([
    [10],
    [15],
    [20]
], dtype=np.float32)

# Convert to tensors
X_train = torch.tensor(X)
y_train = torch.tensor(y)

# ---- Model Definition ----
class EcoModel(nn.Module):
    def __init__(self):
        super(EcoModel, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x):
        return self.net(x)

model = EcoModel()

# ---- Training Setup ----
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# ---- Training Loop ----
epochs = 200

for epoch in range(epochs):
    model.train()

    outputs = model(X_train)
    loss = criterion(outputs, y_train)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 50 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item()}")

# ---- Save Model ----
torch.save(model.state_dict(), "models/eco_model.pth")

import datetime
next_run = datetime.datetime.now() + datetime.timedelta(seconds=600)
print(f"PyTorch model trained and saved! Next scheduled automated run would occur around: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
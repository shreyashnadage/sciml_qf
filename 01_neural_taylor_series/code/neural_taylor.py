import torch
from pathlib import Path
import torch.nn as nn
import torch.optim as optim
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

# 1. THE ORACLE: Analytical Black-Scholes
def black_scholes_call(S, K, T, sigma, r):
    if T <= 1e-4: return np.maximum(S - K, 0.0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

# Generate grid
S_vals = np.linspace(50, 150, 40)
T_vals = np.linspace(0.01, 1.0, 40)
S_grid, T_grid = np.meshgrid(S_vals, T_vals)
V_true = np.array([[black_scholes_call(s, 100, t, 0.2, 0.05) for s in S_vals] for t in T_vals])

X_train = torch.tensor(np.vstack([S_grid.ravel(), T_grid.ravel()]).T, dtype=torch.float32)
y_train = torch.tensor(V_true.ravel().reshape(-1, 1), dtype=torch.float32)

# 2. THE ELASTIC SHEET: Neural Architecture
class OptionSurfaceNet(nn.Module):
    def __init__(self):
        super(OptionSurfaceNet, self).__init__()
        self.sheet = nn.Sequential(
            nn.Linear(2, 64),
            nn.Tanh(),        # Smooth Hinge
            nn.Linear(64, 64),
            nn.Tanh(),        # Smooth Hinge
            nn.Linear(64, 1)
        )
    def forward(self, x): return self.sheet(x)

model = OptionSurfaceNet()
optimizer = optim.Adam(model.parameters(), lr=0.01)
criterion = nn.MSELoss()

# 3. THE TRAINING LOOP: Pinning it down
for epoch in range(1001):
    optimizer.zero_grad()
    predictions = model(X_train)
    loss = criterion(predictions, y_train)
    loss.backward()
    optimizer.step()
    if epoch % 200 == 0: print(f"Epoch {epoch} | Loss: {loss.item():.4f}")

# 4. GENERATING PLOTLY ARTIFACT
V_pred = model(X_train).detach().numpy().reshape(S_grid.shape)
fig = go.Figure(data=[
    go.Surface(z=V_true, x=S_grid, y=T_grid, colorscale='Blues', opacity=0.5, name='True'),
    go.Surface(z=V_pred, x=S_grid, y=T_grid, colorscale='Oranges', opacity=0.9, name='Sheet')
])
fig.write_html(str(Path(__file__).resolve().parent / "surface_fit.html"))
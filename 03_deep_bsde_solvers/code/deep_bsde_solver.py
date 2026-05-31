import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

# Set seed for reproducible video results
torch.manual_seed(42)
np.random.seed(42)

# ==============================================================================
# 1. THE MARKET ENVIRONMENT (Parameters & Simulation)
# ==============================================================================
num_assets = 50        # d = 50 dimensions
num_steps = 50         # 50 time steps
dt = 1.0 / num_steps   # Time step size (Total T = 1 year)
batch_size = 1000      # Number of paths per training step

r = 0.05               # Risk-free rate
sigma = 0.20           # Volatility
S0 = 100.0             # Initial stock price
K = 100.0              # Strike price

def simulate_market(batch_size):
    """Generates 50-dimensional Brownian motion and Stock paths."""
    dW = torch.randn(batch_size, num_steps, num_assets) * np.sqrt(dt)
    S = torch.zeros(batch_size, num_steps + 1, num_assets)
    S[:, 0, :] = S0
    
    # Forward SDE: Geometric Brownian Motion
    for t in range(num_steps):
        S[:, t+1, :] = S[:, t, :] * torch.exp(
            (r - 0.5 * sigma**2) * dt + sigma * dW[:, t, :]
        )
    return S, dW

# ==============================================================================
# 2. THE DEEP BSDE ARCHITECTURE (The Hedging Game)
# ==============================================================================
class DeepBSDE(nn.Module):
    def __init__(self):
        super(DeepBSDE, self).__init__()
        # The Master Dial: Initial guess for the option price
        self.Y_0 = nn.Parameter(torch.tensor([1.0]))
        
        # The Algorithmic Trader: Neural Network predicting Z_t (Delta)
        self.agent = nn.Sequential(
            nn.Linear(num_assets + 1, 256),
            nn.Tanh(),
            nn.Linear(256, 256),
            nn.Tanh(),
            nn.Linear(256, num_assets)
        )

    def forward(self, S, dW):
        Y = self.Y_0.expand(batch_size) # Start with initial cash
        
        # Unroll the game through time
        for t in range(num_steps):
            time_input = torch.full((batch_size, 1), t * dt)
            current_S = S[:, t, :]
            
            # Agent observes market and outputs hedging vector Z
            inputs = torch.cat([time_input, current_S], dim=1)
            Z = self.agent(inputs)
            
            # Update Wealth Ledger: dY = r*Y*dt + Z*dW
            Z_dW = torch.sum(Z * dW[:, t, :], dim=1)
            Y = Y + (r * Y * dt) + Z_dW
            
        return Y # Final Wealth at expiration T

# ==============================================================================
# 3. THE TRAINING LOOP (Backpropagation)
# ==============================================================================
model = DeepBSDE()
optimizer = optim.Adam(model.parameters(), lr=0.01)

print("Training the Deep BSDE Solver...")
for epoch in range(1500):
    optimizer.zero_grad()
    
    # Step 1: Simulate random paths
    S, dW = simulate_market(batch_size)
    
    # Step 2: Play the game to get Terminal Wealth
    Y_terminal = model(S, dW)
    
    # Step 3: Calculate True Payoff (Geometric Basket)
    # Payoff = max( GeometricAverage(S_T) - K, 0 )
    log_sum = torch.sum(torch.log(S[:, -1, :]), dim=1)
    geometric_avg = torch.exp(log_sum / num_assets)
    true_payoff = torch.relu(geometric_avg - K)
    
    # Step 4: The Time-Travel Penalty (Loss)
    loss = torch.nn.MSELoss()(Y_terminal, true_payoff)
    loss.backward()
    optimizer.step()
    
    if epoch % 300 == 0:
        print(f"Epoch {epoch} | Loss: {loss.item():.4f} | Y_0 (Price): {model.Y_0.item():.4f}")

# ==============================================================================
# 4. INFERENCE & BENCHMARKING (The Final Proof)
# ==============================================================================
print(f"\nFinal Deep BSDE Price: {model.Y_0.item():.4f}")

# Analytical Black-Scholes formula for Geometric Basket Option
sigma_G = sigma / np.sqrt(num_assets)
mu_G = r - 0.5 * sigma**2 + 0.5 * sigma_G**2
d1 = (np.log(S0 / K) + (mu_G + 0.5 * sigma_G**2) * 1.0) / sigma_G
d2 = d1 - sigma_G
analytical_price = np.exp(-r * 1.0) * (S0 * np.exp(mu_G * 1.0) * norm.cdf(d1) - K * norm.cdf(d2))

print(f"Analytical True Price: {analytical_price:.4f}")

# Generate the Scatter Plot Artifact
S_test, dW_test = simulate_market(1000)
with torch.no_grad():
    Y_pred = model(S_test, dW_test).numpy()
    
log_sum_test = torch.sum(torch.log(S_test[:, -1, :]), dim=1)
true_payoff_test = torch.relu(torch.exp(log_sum_test / num_assets) - K).numpy()

fig = go.Figure()
# The Ideal Y=X Line
fig.add_trace(go.Scatter(x=[0, 15], y=[0, 15], mode='lines', name='Perfect Replication (Y=X)', line=dict(color='white', width=2, dash='dash')))
# The Neural Network's Performance
fig.add_trace(go.Scatter(x=true_payoff_test, y=Y_pred, mode='markers', name='Deep BSDE Wealth', marker=dict(color='cyan', size=4, opacity=0.6)))

fig.update_layout(title="Deep BSDE Replication Performance (50 Assets)", xaxis_title="True Analytical Payoff at T", yaxis_title="Neural Network Terminal Wealth (Y_T)", template="plotly_dark")
import os
output_dir = os.path.dirname(os.path.abspath(__file__))
fig.write_html(os.path.join(output_dir, "bsde_scatter.html"))
fig.write_image(os.path.join(output_dir, "bsde_scatter.png"))
print("Saved scatter plot artifacts (HTML and PNG).")
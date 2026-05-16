# ==============================================================================
# SCI-ML FOR QUANT FINANCE: MODULE 3
# TARGET: Deep BSDE Solver for 100-Dimensional Basket Options
# ==============================================================================

import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

# Financial Parameters for a 100-Asset Basket
d = 100           # Number of assets (Dimensions)
r = 0.05          # Risk-free rate
sigma = 0.2       # Volatility (Constant for simplicity)
T = 1.0           # Time to maturity
N_steps = 20      # Number of time steps for Euler-Maruyama
dt = T / N_steps
batch_size = 256  # Number of simulated paths per training step

torch.manual_seed(42)

# ------------------------------------------------------------------------------
# STEP 1: The Hedging Network (The "Agent")
# ------------------------------------------------------------------------------
class DeepBSDE_Agent(nn.Module):
    def __init__(self, d):
        super(DeepBSDE_Agent, self).__init__()
        # Input: Current time (1) + Stock Prices (d) -> Output: Deltas for each stock (d)
        self.net = nn.Sequential(
            nn.Linear(d + 1, 128),
            nn.Tanh(),              # Smooth activations are still critical!
            nn.Linear(128, 128),
            nn.Tanh(),
            nn.Linear(128, d)       # Outputs 100 Deltas (one for each asset)
        )
        
        # THE MAGIC TRICK: The initial option price is just a trainable parameter!
        # We guess it starts at 0.0, and the optimizer will find the true price.
        self.V_0 = nn.Parameter(torch.tensor([0.0])) 

    def forward(self, t, S):
        # Concatenate time and spot prices
        t_vec = torch.ones(S.shape[0], 1) * t
        x = torch.cat([t_vec, S], dim=1)
        return self.net(x) # Returns Delta_t

# ------------------------------------------------------------------------------
# STEP 2: The Forward Stochastic Simulation
# ------------------------------------------------------------------------------
def run_simulation(model, batch_size):
    # Initialize stock prices at S_0 = 100 for all 100 assets
    S_t = torch.ones(batch_size, d) * 100.0
    
    # Initialize the bank account (Wealth) with our guessed option price
    W_t = model.V_0.expand(batch_size, 1) 
    
    # Step forward in time
    for step in range(N_steps):
        t = step * dt
        
        # 1. The Agent looks at the market and decides the Deltas
        delta_t = model(t, S_t)
        
        # 2. The Market moves (Geometric Brownian Motion)
        dW = torch.randn(batch_size, d) * torch.sqrt(torch.tensor(dt))
        S_next = S_t * (1 + r * dt + sigma * dW)
        
        # 3. Our Wealth changes based on our Deltas and the risk-free rate
        # W_{t+1} = W_t + Bank Interest + Profit/Loss from Stock Hedging
        bank_interest = r * (W_t - torch.sum(delta_t * S_t, dim=1, keepdim=True)) * dt
        stock_pnl = torch.sum(delta_t * (S_next - S_t), dim=1, keepdim=True)
        
        W_t = W_t + bank_interest + stock_pnl
        S_t = S_next
        
    return S_t, W_t

# ------------------------------------------------------------------------------
# STEP 3: The Terminal Payoff (The "Target")
# ------------------------------------------------------------------------------
def basket_call_payoff(S_T, strike=100.0):
    # Payoff is based on the average price of the 100 assets
    basket_avg = torch.mean(S_T, dim=1, keepdim=True)
    return torch.relu(basket_avg - strike)

# ------------------------------------------------------------------------------
# STEP 4: The Training Loop
# ------------------------------------------------------------------------------
def train_deep_bsde(epochs=1500):
    model = DeepBSDE_Agent(d)
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    print("Starting Deep BSDE solver training...")
    for epoch in range(epochs):
        optimizer.zero_grad()
        
        # Run the simulation from t=0 to t=T
        S_T, W_T = run_simulation(model, batch_size)
        
        # Calculate the true payoff we OWE the option buyer
        True_Payoff = basket_call_payoff(S_T)
        
        # The Loss is the mismatch between our Hedged Wealth and the True Payoff
        loss = torch.mean((W_T - True_Payoff)**2)
        
        loss.backward()
        optimizer.step()
        
        if epoch % 300 == 0:
            print(f"Epoch {epoch:04d} | Loss: {loss.item():.4f} | Current Price Guess (V_0): {model.V_0.item():.4f}")

    print(f"\nFinal Predicted 100D Basket Option Price: {model.V_0.item():.4f}")
    return model

if __name__ == "__main__":
    trained_model = train_deep_bsde()

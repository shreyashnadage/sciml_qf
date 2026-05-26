import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from scipy.stats import norm
import os

# Set random seed for reproducibility
torch.manual_seed(42)

# Financial Parameters
K = 100.0      # Strike Price
r = 0.05       # Risk-free rate (5%)
sigma = 0.20   # Volatility (20%)
T_max = 1.0    # Time to maturity (1 year)
S_min = 50.0   # Minimum stock price
S_max = 150.0  # Maximum stock price

class PINN(nn.Module):
    def __init__(self):
        super(PINN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )

    def forward(self, S, t):
        inputs = torch.cat([S, t], dim=1)
        return self.net(inputs)

def sample_domain(num_points=5000):
    S_colloc = torch.empty(num_points, 1).uniform_(S_min, S_max)
    t_colloc = torch.empty(num_points, 1).uniform_(0.0, T_max)
    S_colloc.requires_grad_()
    t_colloc.requires_grad_()
    return S_colloc, t_colloc

def sample_boundary(num_points=1000):
    S_bound = torch.empty(num_points, 1).uniform_(S_min, S_max)
    t_bound = torch.ones(num_points, 1) * T_max
    payoff = torch.relu(S_bound - K)
    return S_bound, t_bound, payoff

def calculate_physics_loss(model, S, t):
    V = model(S, t)
    
    dV_dS = torch.autograd.grad(V, S, grad_outputs=torch.ones_like(V), create_graph=True)[0]
    d2V_dS2 = torch.autograd.grad(dV_dS, S, grad_outputs=torch.ones_like(dV_dS), create_graph=True)[0]
    dV_dt = torch.autograd.grad(V, t, grad_outputs=torch.ones_like(V), create_graph=True)[0]
    
    pde_residual = dV_dt + 0.5 * sigma**2 * S**2 * d2V_dS2 + r * S * dV_dS - r * V
    return torch.mean(pde_residual**2)

if __name__ == "__main__":
    model = PINN()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    epochs = 2000
    
    print("Training PINN...")
    for epoch in range(epochs):
        optimizer.zero_grad()
        S_colloc, t_colloc = sample_domain()
        loss_physics = calculate_physics_loss(model, S_colloc, t_colloc)
        
        S_bound, t_bound, true_payoff = sample_boundary()
        V_bound = model(S_bound, t_bound)
        loss_boundary = torch.mean((V_bound - true_payoff)**2)
        
        total_loss = loss_physics + loss_boundary
        total_loss.backward()
        optimizer.step()
        
        if epoch % 400 == 0:
            print(f"Epoch {epoch:4d} | Loss: {total_loss.item():.4f}")
            
    print("Training Complete. Saving model...")
    # Determine the directory path of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "pinn_model.pth")
    torch.save(model.state_dict(), model_path)
    print(f"Saved weights to: {model_path}")

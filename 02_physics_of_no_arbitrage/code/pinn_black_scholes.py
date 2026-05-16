# ==============================================================================
# SCI-ML FOR QUANT FINANCE: MODULE 2
# TARGET: Physics-Informed Neural Network (PINN) for Black-Scholes PDE
# ==============================================================================

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Set random seeds for exact reproducibility
torch.manual_seed(42)
np.random.seed(42)

# Financial Parameters (The "Rules of the Game")
K = 50.0       # Strike Price
r = 0.05       # Risk-free rate
sigma = 0.2    # Volatility
T_max = 1.0    # 1 Year to maturity

# ------------------------------------------------------------------------------
# STEP 1: Domain Definition & Collocation Points (NO LABELS, JUST COORDINATES)
# ------------------------------------------------------------------------------
def generate_collocation_points(N_collocation=10000):
    # Randomly sample S and t in our domain
    S_colloc = torch.rand(N_collocation, 1) * 150.0 + 0.1  # Avoid exact 0
    t_colloc = torch.rand(N_collocation, 1) * T_max
    
    # CRITICAL: We must tell PyTorch to track gradients for these input coordinates
    S_colloc.requires_grad = True
    t_colloc.requires_grad = True
    
    return S_colloc, t_colloc

def generate_boundary_points(N_boundary=2000):
    # Terminal Boundary: t = T_max (Expiration)
    S_term = torch.rand(N_boundary, 1) * 150.0
    t_term = torch.ones_like(S_term) * T_max
    # The absolute truth at expiration: Payoff = Max(S-K, 0)
    V_term_true = torch.relu(S_term - K) 
    return S_term, t_term, V_term_true

# ------------------------------------------------------------------------------
# STEP 2: The Neural Surface Engine
# ------------------------------------------------------------------------------
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
        # We concatenate S and t into a single input vector
        x = torch.cat([S, t], dim=1)
        return self.net(x)

# ------------------------------------------------------------------------------
# STEP 3: The Physics Loss Function (The "Teacher")
# ------------------------------------------------------------------------------
def physics_loss(model, S, t):
    # 1. Forward Pass: Get the network's current guess for V
    V = model(S, t)
    
    # 2. Extract Gradients (The Greeks)
    # dV/dt (Time Decay / Theta)
    # Note: Using create_graph=True to allow higher-order derivatives
    dV_dt = torch.autograd.grad(V, t, grad_outputs=torch.ones_like(V), 
                                create_graph=True)[0]
    
    # dV/dS (Delta)
    dV_dS = torch.autograd.grad(V, S, grad_outputs=torch.ones_like(V), 
                                create_graph=True)[0]
    
    # d2V/dS2 (Gamma) - The derivative of the derivative
    d2V_dS2 = torch.autograd.grad(dV_dS, S, grad_outputs=torch.ones_like(dV_dS), 
                                  create_graph=True)[0]
    
    # 3. Construct the Black-Scholes PDE Residual
    # If the network follows the rules, this equation should equal 0
    # PDE: dV/dt + 0.5 * sigma^2 * S^2 * d2V/dS2 + r*S*dV/dS - r*V = 0
    pde_residual = dV_dt + 0.5 * (sigma**2) * (S**2) * d2V_dS2 + r * S * dV_dS - r * V
    
    # 4. The Loss is the Mean Squared Error of the residual away from 0
    return torch.mean(pde_residual**2)

# ------------------------------------------------------------------------------
# STEP 4: Training the PINN
# ------------------------------------------------------------------------------
def train_pinn(epochs=3000):
    model = PINN()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    S_colloc, t_colloc = generate_collocation_points()
    S_term, t_term, V_term_true = generate_boundary_points()
    
    print("Starting training loop to enforce the laws of finance...")

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        # 1. Calculate how much the network violates the PDE inside the domain
        loss_pde = physics_loss(model, S_colloc, t_colloc)
        
        # 2. Calculate how much the network violates the Terminal Payoff
        V_term_pred = model(S_term, t_term)
        loss_term = torch.mean((V_term_pred - V_term_true)**2)
        
        # 3. Total Loss: Physics + Boundaries
        total_loss = loss_pde + loss_term
        
        total_loss.backward()
        optimizer.step()
        
        if epoch % 500 == 0:
            print(f"Epoch {epoch:04d} | PDE Loss: {loss_pde.item():.6f} | Boundary Loss: {loss_term.item():.6f}")

    print("Training Complete. Physics-Informed Engine is ready.")
    return model

# ------------------------------------------------------------------------------
# STEP 5: Analytical Comparison (Sanity Check)
# ------------------------------------------------------------------------------
def black_scholes_analytical(S, K, T, sigma, r):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def validate_pinn(model):
    model.eval()
    S_test = np.linspace(10, 100, 100)
    t_fixed = 0.5 # 6 months to maturity
    
    S_tensor = torch.tensor(S_test, dtype=torch.float32).reshape(-1, 1)
    t_tensor = torch.ones_like(S_tensor) * t_fixed
    
    with torch.no_grad():
        V_pinn = model(S_tensor, t_tensor).numpy()
    
    V_true = np.array([black_scholes_analytical(s, K, T_max - t_fixed, sigma, r) for s in S_test])
    
    plt.figure(figsize=(10, 5), facecolor='#111111')
    ax = plt.axes()
    ax.set_facecolor('#111111')
    plt.plot(S_test, V_true, label='Analytical (Black-Scholes)', color='#0000FF', linewidth=3)
    plt.plot(S_test, V_pinn, '--', label='PINN Prediction', color='#FFA500', linewidth=2)
    plt.title(f'PINN Validation at t={t_fixed}', color='white')
    plt.xlabel('Stock Price (S)', color='white')
    plt.ylabel('Option Value (V)', color='white')
    ax.tick_params(colors='white')
    plt.legend()
    plt.grid(color='#333333', linestyle='--')
    plt.savefig('D:/SCIML_QF/02_physics_of_no_arbitrage/media/pinn_validation.png')
    print("Validation plot saved to media/pinn_validation.png")

if __name__ == "__main__":
    trained_model = train_pinn()
    validate_pinn(trained_model)

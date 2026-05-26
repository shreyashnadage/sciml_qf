import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

# Set random seed for reproducibility
torch.manual_seed(42)

# ==============================================================================
# FINANCIAL PARAMETERS
# ==============================================================================
K = 100.0      # Strike Price
r = 0.05       # Risk-free rate (5%)
sigma = 0.20   # Volatility (20%)
T_max = 1.0    # Time to maturity (1 year)
S_min = 50.0   # Minimum stock price in our domain
S_max = 150.0  # Maximum stock price in our domain

# ==============================================================================
# 1. THE ELASTIC SHEET (Neural Architecture)
# ==============================================================================
class PINN(nn.Module):
    def __init__(self):
        super(PINN, self).__init__()
        # 2 Inputs (S, t) -> 1 Output (Option Value V)
        self.net = nn.Sequential(
            nn.Linear(2, 64),
            nn.Tanh(),        # The smooth hinge: absolutely critical for 2nd derivatives
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )

    def forward(self, S, t):
        # Concatenate S and t to feed into the network
        inputs = torch.cat([S, t], dim=1)
        return self.net(inputs)

# ==============================================================================
# 2. THE EMPTY ROOM (Domain & Boundary Sampling)
# ==============================================================================
def sample_domain(num_points=5000):
    # Randomly scatter points across Space (S) and Time (t)
    S_colloc = torch.empty(num_points, 1).uniform_(S_min, S_max)
    t_colloc = torch.empty(num_points, 1).uniform_(0.0, T_max)
    
    # CRITICAL: Tell PyTorch to track the gradients of these inputs!
    S_colloc.requires_grad_()
    t_colloc.requires_grad_()
    
    return S_colloc, t_colloc

def sample_boundary(num_points=1000):
    # At expiration (t = T_max), the option value MUST equal the hockey stick payoff.
    S_bound = torch.empty(num_points, 1).uniform_(S_min, S_max)
    t_bound = torch.ones(num_points, 1) * T_max # Time is locked at expiration
    
    # The true reality of a European Call option at expiration
    payoff = torch.relu(S_bound - K) 
    
    return S_bound, t_bound, payoff

# ==============================================================================
# 3. THE EQUILIBRIUM SCALE (Physics Loss via Autograd)
# ==============================================================================
def calculate_physics_loss(model, S, t):
    # Ask the network for its current guess
    V = model(S, t)
    
    # Extract Delta (dV/dS)
    dV_dS = torch.autograd.grad(
        V, S, 
        grad_outputs=torch.ones_like(V), 
        create_graph=True
    )[0]
    
    # Extract Gamma (d2V/dS2)
    d2V_dS2 = torch.autograd.grad(
        dV_dS, S, 
        grad_outputs=torch.ones_like(dV_dS), 
        create_graph=True
    )[0]
    
    # Extract Theta (dV/dt)
    dV_dt = torch.autograd.grad(
        V, t, 
        grad_outputs=torch.ones_like(V), 
        create_graph=True
    )[0]
    
    # The Black-Scholes PDE Residual
    pde_residual = dV_dt + 0.5 * sigma**2 * S**2 * d2V_dS2 + r * S * dV_dS - r * V
    
    # Loss is how far the residual is from zero (MSE)
    return torch.mean(pde_residual**2)

# ==============================================================================
# 4. PINNING IT IN THE DARK (The Training Loop)
# ==============================================================================
model = PINN()
optimizer = optim.Adam(model.parameters(), lr=0.001)

epochs = 2000
print("Locking network in the empty room. Beginning PDE optimization...")

for epoch in range(epochs):
    optimizer.zero_grad()
    
    # Step A: Sample the space and calculate Physics Loss
    S_colloc, t_colloc = sample_domain()
    loss_physics = calculate_physics_loss(model, S_colloc, t_colloc)
    
    # Step B: Sample the boundary and calculate Boundary Loss
    S_bound, t_bound, true_payoff = sample_boundary()
    V_bound = model(S_bound, t_bound)
    loss_boundary = torch.mean((V_bound - true_payoff)**2)
    
    # Step C: Total Loss is the sum of physics tension and boundary adherence
    total_loss = loss_physics + loss_boundary
    
    # Pull the sheet tighter
    total_loss.backward()
    optimizer.step()
    
    if epoch % 400 == 0:
        print(f"Epoch {epoch:4d} | Total Loss: {total_loss.item():.4f} | PDE Res: {loss_physics.item():.4f} | Bound: {loss_boundary.item():.4f}")

print("Training Complete.")

# ==============================================================================
# 5. VISUALIZING THE DISCOVERY (Plotly Artifact)
# ==============================================================================
print("Generating visualization artifact...")

# Create a grid for visualization
S_grid_vals = np.linspace(S_min, S_max, 40)
t_grid_vals = np.linspace(0.01, T_max, 40)
S_mesh, t_mesh = np.meshgrid(S_grid_vals, t_grid_vals)

S_tensor = torch.tensor(S_mesh.ravel(), dtype=torch.float32).unsqueeze(1)
t_tensor = torch.tensor(t_mesh.ravel(), dtype=torch.float32).unsqueeze(1)

# Ask the PINN for the surface it discovered
with torch.no_grad():
    V_pred = model(S_tensor, t_tensor).numpy().reshape(S_mesh.shape)

# Analytical Black-Scholes (For comparison only - the model never saw this!)
def black_scholes_analytical(S, K, T, sigma, r):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

V_true = np.zeros_like(S_mesh)
for i in range(S_mesh.shape[0]):
    for j in range(S_mesh.shape[1]):
        V_true[i,j] = black_scholes_analytical(S_mesh[i,j], K, t_mesh[i,j], sigma, r)

# Generate the 3D Plotly Figure
fig = go.Figure()

# Plot the True Mathematical Surface (Blue)
fig.add_trace(go.Surface(
    z=V_true, x=S_mesh, y=t_mesh, 
    colorscale='Blues', opacity=0.5, name='True Analytical Surface',
    showscale=False
))

# Plot the PINN Discovered Surface (Orange)
fig.add_trace(go.Surface(
    z=V_pred, x=S_mesh, y=t_mesh, 
    colorscale='Oranges', opacity=0.9, name='PINN Discovered Surface',
    showscale=False
))

fig.update_layout(
    title='PINN Discovery vs True Black-Scholes Surface',
    scene=dict(
        xaxis_title='Stock Price (S)',
        yaxis_title='Time to Maturity (t)',
        zaxis_title='Option Value (V)',
        camera=dict(eye=dict(x=1.5, y=-1.5, z=1.0))
    ),
    margin=dict(l=0, r=0, b=0, t=40)
)

fig.write_html("surface_fit.html")
print("Saved 'surface_fit.html'. Open this file in your browser to explore the 3D surface!")
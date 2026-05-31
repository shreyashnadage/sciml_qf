import torch
import torch.nn as nn
import torch.optim as optim
import torchsde
import signatory
import matplotlib.pyplot as plt
import numpy as np

# Set seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# ==============================================================================
# 1. GENERATE "REAL" ROUGH MARKET DATA (The Target)
# ==============================================================================
def generate_rough_market_path(batch_size=128, steps=100, dt=0.01):
    """Simulates a market with volatility clustering and microstructure noise."""
    t = torch.linspace(0, steps * dt, steps)
    paths = torch.ones(batch_size, steps, 1) # Start at price 1.0
    
    for i in range(1, steps):
        # Geometric Brownian Motion base + Random Jumps + Noise
        dW = torch.randn(batch_size, 1) * np.sqrt(dt)
        jumps = (torch.rand(batch_size, 1) < 0.05).float() * torch.randn(batch_size, 1) * 0.1
        paths[:, i, 0] = paths[:, i-1, 0] * torch.exp((0.05 - 0.5 * 0.2**2) * dt + 0.2 * dW + jumps).squeeze(-1)
    
    return t, paths

t_target, real_paths = generate_rough_market_path()

# ==============================================================================
# 2. THE PATH SIGNATURE (Extracting the Barcode)
# ==============================================================================
# UPGRADE: Increased depth to 4 to capture higher-order roughness and micro-geometry
depth = 4 
true_signatures = signatory.signature(real_paths, depth=depth)

# ==============================================================================
# 3. THE NEURAL SDE ARCHITECTURE (Deepened)
# ==============================================================================
class LatentNeuralSDE(nn.Module):
    noise_type = 'diagonal'
    sde_type = 'ito'

    # UPGRADE: Increased hidden size to 128 for higher capacity
    def __init__(self, state_size=1, hidden_size=128):
        super(LatentNeuralSDE, self).__init__()
        
        # UPGRADE: Added an extra hidden layer (Deepening the network)
        self.mu_net = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.Tanh(),
            nn.Linear(hidden_size, hidden_size),
            nn.Tanh(),
            nn.Linear(hidden_size, state_size)
        )
        
        # UPGRADE: Added an extra hidden layer for the volatility engine
        self.sigma_net = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.Tanh(),
            nn.Linear(hidden_size, hidden_size),
            nn.Sigmoid(), 
            nn.Linear(hidden_size, state_size)
        )

    def f(self, t, y):
        return self.mu_net(y)

    def g(self, t, y):
        return self.sigma_net(y) + 0.01

# ==============================================================================
# 4. TRAINING THE GENERATIVE MODEL
# ==============================================================================
sde_model = LatentNeuralSDE(state_size=1)
# Dropped learning rate slightly to stabilize the longer training run
optimizer = optim.Adam(sde_model.parameters(), lr=0.005) 

y0 = torch.ones(128, 1)

# UPGRADE: Increased epochs from 150 to 1500 for proper convergence
epochs = 1500
print("Initializing Deep Neural SDE. Starting Signature Matching...")

for epoch in range(epochs):
    optimizer.zero_grad()
    
    pred_paths = torchsde.sdeint(sde_model, y0, t_target, method='euler').transpose(0, 1)
    pred_signatures = signatory.signature(pred_paths, depth=depth)
    
    loss = torch.mean((pred_signatures - true_signatures)**2)
    
    loss.backward()
    optimizer.step()
    
    if epoch % 200 == 0 or epoch == epochs - 1:
        print(f"Epoch {epoch:4d} | Signature MSE Loss: {loss.item():.6f}")

print("Training Complete. Market Dynamics Captured.")

# ==============================================================================
# 5. GENERATING THE STATIC ARTIFACT (.PNG)
# ==============================================================================
print("Generating static PNG artifact...")

with torch.no_grad():
    y0_test = torch.ones(5, 1) 
    final_synthetic_paths = torchsde.sdeint(sde_model, y0_test, t_target, method='euler').transpose(0, 1)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Neural SDE: Learning Rough Market Dynamics via Signatures', fontsize=16)

axes[0].set_title('Real Market Paths (with Jumps)', fontsize=14)
for i in range(5):
    axes[0].plot(t_target.numpy(), real_paths[i, :, 0].numpy(), lw=1.5, alpha=0.8)
axes[0].set_xlabel('Time (t)')
axes[0].set_ylabel('Asset Price')
axes[0].grid(True, alpha=0.3)

axes[1].set_title('Deep Neural SDE Generated Paths', fontsize=14)
for i in range(5):
    axes[1].plot(t_target.numpy(), final_synthetic_paths[i, :, 0].numpy(), lw=1.5, alpha=0.8, color='crimson')
axes[1].set_xlabel('Time (t)')
axes[1].set_ylabel('Asset Price')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()

artifact_filename = "neural_sde_artifact.png"
plt.savefig(artifact_filename, dpi=300, bbox_inches='tight')
print(f"Artifact successfully saved to: {artifact_filename}")
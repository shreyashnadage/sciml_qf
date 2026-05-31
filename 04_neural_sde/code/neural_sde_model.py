import torch
import torch.nn as nn
import torchsde
import signatory

# Generate Target Path
def generate_rough_market_path(batch_size=128, steps=100, dt=0.01):
    t = torch.linspace(0, steps * dt, steps)
    paths = torch.ones(batch_size, steps, 1)
    for i in range(1, steps):
        dW = torch.randn(batch_size, 1) * torch.sqrt(torch.tensor(dt))
        paths[:, i, 0] = paths[:, i-1, 0] * torch.exp(0.2 * dW)
    return t, paths

t_target, real_paths = generate_rough_market_path()
depth = 3

# =========================================
# 1. Calculate Path Signatures
# =========================================

# Calculate the path signature using signatory
true_signatures = signatory.signature(
    real_paths, depth=depth)

# =========================================
# 2. Latent Neural SDE Architecture
# =========================================

class LatentNeuralSDE(nn.Module):
    noise_type = 'diagonal'
    sde_type = 'ito'
    def __init__(self, state_size=1, hidden_size=32):
        super(LatentNeuralSDE, self).__init__()
        self.mu_net = nn.Sequential(nn.Linear(state_size, hidden_size), nn.Tanh(), nn.Linear(hidden_size, state_size))
        self.sigma_net = nn.Sequential(nn.Linear(state_size, hidden_size), nn.Sigmoid(), nn.Linear(hidden_size, state_size))
    def f(self, t, y): return self.mu_net(y)
    def g(self, t, y): return self.sigma_net(y) + 0.01

# Training step
# Calculate the signature MSE loss
pred_signatures = signatory.signature(pred_paths, depth=depth)
loss = torch.mean((pred_signatures - true_signatures)**2)
loss.backward()

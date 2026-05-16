# ==============================================================================
# SCI-ML FOR QUANT FINANCE: MODULE 1
# TARGET: Universal Function Approximation of the Black-Scholes Surface
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

# ------------------------------------------------------------------------------
# STEP 1: The Analytical Data Generator (Our Ground Truth "Oracle")
# ------------------------------------------------------------------------------
def black_scholes_call(S, K, T, sigma, r):
    """Calculates the analytical European Call Option Price."""
    # Handle the boundary case where option has expired
    if T <= 0:
        return np.maximum(S - K, 0.0)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

# Generate synthetic market scenarios for training
def generate_market_data(num_samples=5000, K=100.0, sigma=0.2, r=0.05):
    # Stock price ranges from 50% of strike to 150% of strike
    S_samples = np.random.uniform(50.0, 150.0, num_samples)
    # Time to maturity ranges from 1 week to 2 years
    T_samples = np.random.uniform(0.01, 2.0, num_samples)
    
    V_samples = np.array([black_scholes_call(s, K, t, sigma, r) for s, t in zip(S_samples, T_samples)])
    
    # Structure inputs as pairs of [S, T]
    X = np.stack([S_samples, T_samples], axis=1)
    y = V_samples.reshape(-1, 1)
    
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

# ------------------------------------------------------------------------------
# STEP 2: Designing the Continuous Differentiable Neural Surface
# ------------------------------------------------------------------------------
class NeuralOptionSurface(nn.Module):
    def __init__(self):
        super(NeuralOptionSurface, self).__init__()
        # We use an explicit architecture designed for smooth surfaces
        self.network = nn.Sequential(
            nn.Linear(2, 64),
            nn.Tanh(),          # CRITICAL: Tanh gives us smooth, continuous derivatives
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 32),
            nn.Tanh(),
            nn.Linear(32, 1)    # Output layer emitting a single scalar: Option Value
        )
        
    def forward(self, x):
        return self.network(x)

# ------------------------------------------------------------------------------
# STEP 3: The Engineering Pipeline
# ------------------------------------------------------------------------------
def train_model():
    # Instantiate data, model, loss function, and optimizer
    X_train, y_train = generate_market_data(num_samples=8000)
    model = NeuralOptionSurface()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.005)

    print("Starting training loop to map the function space...")

    epochs = 1500
    for epoch in range(epochs):
        model.train()
        
        # Forward Pass
        predictions = model(X_train)
        loss = criterion(predictions, y_train)
        
        # Backward Pass & Weights Update
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 200 == 0:
            print(f"Epoch {epoch+1:04d}/{epochs} | Surface MSE Loss: {loss.item():.6f}")

    print("Training Complete. Neural Surface Engine is fully parameterized.")
    return model

# ------------------------------------------------------------------------------
# STEP 4: The Quant Validation Test (Sanity Checking the Surface)
# ------------------------------------------------------------------------------
def validate_model(model):
    model.eval()

    # Create a clean test slice: Stock prices from 50 to 150 at fixed Time to Maturity T=1.0
    S_test = np.linspace(50, 150, 200)
    T_test = np.ones_like(S_test) * 1.0
    X_test = torch.tensor(np.stack([S_test, T_test], axis=1), dtype=torch.float32)

    with torch.no_grad():
        nn_predictions = model(X_test).numpy()

    true_prices = np.array([black_scholes_call(s, 100.0, 1.0, 0.2, 0.05) for s in S_test])

    # Plotting the Verification Curve
    plt.figure(figsize=(10, 5), facecolor='#111111')
    ax = plt.axes()
    ax.set_facecolor('#111111')
    plt.plot(S_test, true_prices, label='Black-Scholes Analytical Price', color='#0000FF', linewidth=3)
    plt.plot(S_test, nn_predictions, '--', label='Neural Surface Prediction', color='#FFA500', linewidth=2)
    plt.title('Validation Check: Neural Network vs. Ground Truth', color='white')
    plt.xlabel('Stock Price (S)', color='white')
    plt.ylabel('Option Value (V)', color='white')
    ax.tick_params(colors='white')
    plt.legend()
    plt.grid(color='#333333', linestyle='--')
    plt.savefig('D:/SCIML_QF/01_neural_taylor_series/media/validation_check.png')
    print("Validation plot saved to media/validation_check.png")
    plt.show()

if __name__ == "__main__":
    trained_model = train_model()
    validate_model(trained_model)

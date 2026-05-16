# Module 2: The Physics of No-Arbitrage

This module explores **Physics-Informed Neural Networks (PINNs)** to solve the Black-Scholes Partial Differential Equation (PDE) without any training data.

## Contents
- `code/pinn_black_scholes.py`: PyTorch implementation of the PINN model.
- `manim/scenes.py`: Manim script for visual intuition of PDEs as heat diffusion.
- `media/`: Directory for rendered assets and PINN validation plots.

## Key Concepts
- **Automatic Differentiation**: Extracting gradients (Delta, Gamma) directly from the neural network weights.
- **PDE Residual Loss**: Penalizing the network for violating the Black-Scholes PDE.
- **Collocation Points**: Random points in the domain where the physics are enforced.
- **Boundary Conditions**: Anchoring the model to the terminal payoff (Expiration).

## How to Run

### 1. Training the PINN
Activate the environment:
```powershell
conda activate D:\SCIML_QF\env
```
Run the PINN solver:
```powershell
python code/pinn_black_scholes.py
```

### 2. Rendering Animations
Render the cinematic scenes:
```powershell
# Act 1: The Empty Room
manim -pql manim/scenes.py EmptyRoom

# Act 2: Heat Diffusion Intuition
manim -pql manim/scenes.py HeatDiffusion

# Act 3: PINN Architecture
manim -pql manim/scenes.py PINNArchitecture

# Act 5: Final Surface Comparison
manim -pql manim/scenes.py FinalSurface
```

## Homework Challenge
Change the boundary condition in `generate_boundary_points` from a **Call** payoff to a **Put** payoff:
`V_term_true = torch.relu(K - S_term)`
Observe how the same PDE generates a completely different surface.

# Module 3: Breaking the 100-Dimensional Barrier (Deep BSDE Solvers)

This module demonstrates how to solve high-dimensional pricing problems (e.g., 100-asset baskets) using **Deep Backward Stochastic Differential Equation (BSDE) solvers**.

## Contents
- `code/deep_bsde_solver.py`: PyTorch implementation of the Deep BSDE agent.
- `manim/scenes.py`: Manim script for visual intuition on the Feynman-Kac formula and the Curse of Dimensionality.
- `media/voiceover/voiceover.md`: The cinematic script for the module.

## Key Concepts
- **Curse of Dimensionality**: Why grid-based methods (PDE solvers) fail as the number of assets grows.
- **Feynman-Kac Formula**: The mathematical bridge between PDEs and Stochastic Differential Equations (SDEs).
- **Hedging as Reinforcement Learning**: Training a neural network to minimize the "hedging error" along random market paths.
- **V0 Parameter**: Learning the price of an option as a trainable model parameter.

## How to Run

### 1. Training the Solver
Activate the environment:
```powershell
conda activate D:\SCIML_QF\env
```
Run the Deep BSDE solver:
```powershell
python code/deep_bsde_solver.py
```

### 2. Rendering Animations
Render the cinematic scenes:
```powershell
manim -pql manim/scenes.py Scene1_CurseOfDimensionality
manim -pql manim/scenes.py Scene2_FeynmanKacPaths
manim -pql manim/scenes.py Scene3_BSDEArchitecture
manim -pql manim/scenes.py Scene4_ConvergenceHistogram
```

## Homework Challenge
Modify `code/deep_bsde_solver.py` to include a **correlation matrix** between the 100 assets. 
1. Change `d = 100` to `d = 50`.
2. Generate a Cholesky decomposition of a random positive-definite correlation matrix.
3. Multiply the Brownian noise `dW` by the Cholesky matrix.
Observe if the network converges faster or slower when assets are highly correlated.

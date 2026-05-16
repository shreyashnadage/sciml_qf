# Module 1: The Neural Taylor Series

This module covers the universal approximation of the Black-Scholes option pricing surface using a neural network with smooth activation functions.

## Contents
- `code/neural_taylor.py`: PyTorch implementation of the neural surface model.
- `manim/scenes.py`: Manim script for cinematic 3D animations of the option surface.
- `media/`: Directory for rendered assets and validation plots.

## How to Run

### 1. Training the Model
Ensure the `manim_env` is activated:
```powershell
conda activate D:\SCIML_QF\env
```
Run the training script:
```powershell
python code/neural_taylor.py
```
This will train the model and save a validation plot in `media/validation_check.png`.

### 2. Rendering Animations
To render the Manim scenes, run:
```powershell
# Opening Payoff (2D)
manim -pql manim/scenes.py OpeningPayoff

# Option Surface Warp (3D)
manim -pql manim/scenes.py OptionSurfaceWarp

# Neural Training Morph (3D)
manim -pql manim/scenes.py NeuralApproximator
```

## Homework Challenge
Change the activation function in `NeuralOptionSurface` from `nn.Tanh()` to `nn.ReLU()` and observe the impact on the surface smoothness and its derivatives.

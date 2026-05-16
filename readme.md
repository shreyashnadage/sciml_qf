# 🪐 SciML for Quant Finance
**Bridging the gap between Stochastic Calculus and Deep Learning.**

[![Presented By](https://img.shields.io/badge/Presented%20By-QuantCatalysts-blueviolet?style=for-the-badge)](https://yourwebsite.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)]()
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)]()
[![Open In Colab](https://img.shields.io/badge/Colab-Ready-F9AB00?style=for-the-badge&logo=googlecolab&color=525252)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)]()

Welcome to the official repository for **SciML for Quant Finance**, a groundbreaking video series and interactive curriculum created by **QuantCatalysts**. 

This course is designed to take you from the foundational concepts of functional approximation to state-of-the-art Deep Stochastic Control and Physics-Informed Neural Networks (PINNs). We move away from pure "black-box" machine learning and instead build architectures that strictly obey the laws of financial physics (no-arbitrage, heat equations, and rough volatility).

---

## 📖 The Paradigm Shift

For decades, numerical finance relied on heavy Monte Carlo simulations and rigid finite-difference grids. But what happens when a desk needs to price a basket of 100 correlated assets? Traditional grids explode—a mathematical phenomenon known as the *Curse of Dimensionality*.

**Scientific Machine Learning (SciML)** offers a mesh-free, highly scalable solution. By blending the automatic differentiation engines of modern AI with the rigorous stochastic calculus of quantitative finance, we can solve high-dimensional partial differential equations (PDEs), learn market dynamics directly from data, and optimally hedge portfolios under real-world friction.

---

## 🗂️ Course Curriculum & Interactive Notebooks

Every module in this course is accompanied by a **Zero-Setup Google Colab Notebook**. You don't need to install anything locally; just click the badges below to run the mathematical engines right in your browser.

### [Module 1: The Neural Taylor Series](./modules/module1_universal_approximation)
*Understanding Neural Networks as Universal Function Approximators.*
*   **Concepts:** Universal Approximation Theorem, Black-Scholes Surface Mapping, Smooth Activations ($\tanh$).
*   **Interactive Code:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/QuantCatalysts/SciML-Quant-Finance/blob/main/modules/module1.ipynb)

### [Module 2: The Physics of No-Arbitrage](./modules/module2_pinns)
*Solving the Black-Scholes PDE without any training data.*
*   **Concepts:** Physics-Informed Neural Networks (PINNs), Automatic Differentiation, PDE Residual Loss, Heat Diffusion.
*   **Interactive Code:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/QuantCatalysts/SciML-Quant-Finance/blob/main/modules/module2.ipynb)

### [Module 3: Breaking the 100-Dimensional Barrier](./modules/module3_deep_bsde)
*Pricing a 100-asset basket option where traditional grids fail.*
*   **Concepts:** Deep Backward Stochastic Differential Equations (BSDEs), Feynman-Kac Formula, Reinforcement Learning for Hedging.
*   **Interactive Code:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/QuantCatalysts/SciML-Quant-Finance/blob/main/modules/module3.ipynb)

### [Module 4: Neural SDEs & Market Signatures](./modules/module4_neural_sdes)
*Learning the differential equations of the market directly from data.*
*   **Concepts:** Rough Paths, Path Signatures, Latent Neural Stochastic Differential Equations (SDEs), Generative Market Modeling.
*   **Interactive Code:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/QuantCatalysts/SciML-Quant-Finance/blob/main/modules/module4.ipynb)

### [Module 5: Deep Hedging under Friction](./modules/module5_deep_hedging)
*Moving from textbook pricing to real-world risk management.*
*   **Concepts:** Transaction Costs, Expected Shortfall (CVaR), Recurrent Neural Networks (RNNs) for Optimal Control.
*   **Interactive Code:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/QuantCatalysts/SciML-Quant-Finance/blob/main/modules/module5.ipynb)

### [Module 6: Signature-Informed Transformers](./modules/module6_signature_transformers)
*The modern frontier of rough volatility prediction.*
*   **Concepts:** Transformer Attention Mechanisms, Geometric Memory, Volatility Surface Prediction.
*   **Interactive Code:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/QuantCatalysts/SciML-Quant-Finance/blob/main/modules/module6.ipynb)

---

## 🛠️ Repository Structure

If you wish to clone this repository and run the models locally, here is the architecture:

```text
SciML-Quant-Finance/
│
├── 📂 modules/                   # Google Colab Jupyter Notebooks (.ipynb)
│   ├── module1_universal_approximation.ipynb
│   ├── module2_pinns.ipynb
│   └── ...
│
├── 📂 manim_visuals/             # Manim Python scripts used to generate course animations
│   ├── module1_scenes.py
│   ├── module2_scenes.py
│   └── ...
│
├── 📂 data/                      # Synthetic and historical datasets (if applicable)
├── requirements.txt              # Local Python dependencies
└── README.md
# **Recording Script: Module 2 – The Physics of No-Arbitrage (PINNs)**

**[SCENE 1: A DENSE 3D CLOUD OF GLOWING BLUE DATA POINTS FORMING THE OPTION SURFACE FROM MODULE 1.]**

**(Pacing: Reflective, setting up a confession)**

In our last video, we proved that a neural network can learn the exact shape of a financial derivative.

But we cheated.

We generated ten thousand *perfect* data points using the analytical Black-Scholes formula, and we simply asked our network to memorize that shape.

**[SCENE 2: A SHOCKWAVE SWEEPS THE SCREEN. THE DATA POINTS SHATTER AND FADE. WE ARE LEFT IN A DARK, EMPTY 3D GRID.]**

**(Pacing: Faster, introducing the conflict)**

In the real world of exotic derivatives, or 100-asset basket options, that perfect data doesn't exist. You cannot generate a billion data points to train a model because calculating even *one* point might take hours on a supercomputer.

So, we are faced with the "Empty Room" problem. How do we teach a neural network to price a derivative when we have absolutely zero training data?

**[SCENE 3: PURE WHITE TEXT TYPES OUT IN THE DARKNESS: THE BLACK-SCHOLES PDE.]**

**(Pacing: Deliberate, reverent)**

The answer lies in treating financial mathematics not as a statistical spreadsheet, but as the **laws of physics**.

We don't need data if we know the rules of the game. And in quantitative finance, the ultimate rule is the law of No-Arbitrage. This law is perfectly encapsulated in the Black-Scholes Partial Differential Equation.

Today, we are going to build a Physics-Informed Neural Network, or a PINN. We are going to lock our neural network in this empty room with nothing but this equation. It will have to teach itself how to price an option using *only* the laws of financial physics.

---

**[SCENE 4: FLAT METAL PLATE. A SHARP, JAGGED NEON ORANGE LINE GLOWS IN THE CENTER. IT BEGINS TO "MELT" AND DIFFUSE OUTWARD.]**

**(Pacing: Conversational and illustrative)**

To understand how a neural network can learn from an equation, we need to understand what this equation actually represents. At its core, the Black-Scholes PDE is a variation of the Heat Equation from classical physics.

Imagine a flat metal plate. If you take a blowtorch and heat a very specific, sharp jagged line into the center of it, that heat won't stay concentrated. Over time, it diffuses. It spreads out, seeking equilibrium.

In finance, that jagged blowtorch line is our terminal payoff—the hockey stick at expiration. And just like heat diffuses through metal over time, financial value diffuses through uncertainty.

**[SCENE 5: THE PDE APPEARS. THE SECOND DERIVATIVE TERM (GAMMA) HIGHLIGHTS IN RED. AN ARROW LINKS IT TO THE DIFFUSING HEAT.]**

This term here, the second derivative of value with respect to stock price—our **Gamma**—acts as the diffusion operator. Volatility is the thermal conductivity of our market.

If a financial surface obeys the law of no-arbitrage, all of these moving parts—time decay, diffusion, and drift—must perfectly balance out to equal zero everywhere in space and time. If they don't equal zero, an arbitrage opportunity exists.

---

**[SCENE 6: NEURAL NETWORK GRAPH APPEARS. RED ARROWS LOOP BACKWARDS FROM THE OUTPUT TO AN "AUTOGRAD" BOX.]**

**(Pacing: Instructional, leading to an "aha" moment)**

So, how do we enforce this law? We redefine our neural network's architecture.

We still pass in our stock price and time, and it still outputs an option value. But here is the brilliant twist. Because our neural network is made of smooth, differentiable functions like `Tanh`, we can use a mechanism called **Automatic Differentiation**.

We can ask PyTorch to exactly calculate the gradients of our network's output. We can extract the Delta and the Gamma directly from the network's weights!

**[SCENE 7: THE GREEKS FLOW INTO A BOX LABELED "PDE RESIDUAL LOSS".]**

We take those extracted gradients and plug them right back into the Black-Scholes equation. If the result is exactly zero, the network is obeying the laws of physics. If the result is anything *other* than zero, we call that the "Residual."

Our loss function is no longer the Mean Squared Error against data. Our loss function is the **PDE Residual** itself. We are penalizing the network for breaking the laws of physics.

Let's write the code.

---

**[SCENE 8: SPLIT SCREEN. MANIM BOUNDING BOX ON THE LEFT. COLAB CODE TYPING ON THE RIGHT.]**

**(Pacing: Guiding, technical but accessible)**

Welcome back to Colab.

Notice we are not importing any analytical Black-Scholes formulas to generate data. Instead of data, we need to give the network a space to explore.

We define a domain: stock prices from nearly zero to 150, and time from zero to 1 year. We randomly scatter thousands of coordinate points—called "collocation points"—across this space. The network will evaluate the physics at these exact locations.

Notice the `requires_grad=True` flag in PyTorch. This is the secret to SciML. We are telling PyTorch: *"Watch how these inputs change, because we are going to need their derivatives later."*

We also define our boundary conditions—the walls of our room. At expiration, the value *must* be the hockey stick payoff.

**[SCENE 9: THE FOCUS SHIFTS TO THE AUTOGRAD LOSS FUNCTION IN THE CODE.]**

Here is where the magic happens. We write our custom physics loss function.

We pass our collocation points into the model to get a predicted value. Then, we use `torch.autograd.grad` to crack open the neural network and pull out the first and second derivatives.

We have our physics loss. But physics alone isn't enough. The heat equation tells the network *how* to diffuse, but the boundary conditions tell it *what* is diffusing. Our final training loop simply combines the physics loss with the boundary error.

Let's run the training loop.

---

**[SCENE 10: MASSIVE 3D AXIS. A NEON ORANGE SURFACE SWEEPS INTO EXISTENCE. A BLUE ANALYTICAL SURFACE DROPS ON TOP OF IT, MATCHING FLAWLESSLY.]**

**(Pacing: Triumphant, amazed)**

The loss drops. The network is learning the geometry of the market purely by staring at the PDE. Let's see what it built in the dark.

Look at that. Without a single piece of historical data, without a single Monte Carlo path, our neural network has discovered the exact Black-Scholes option surface. It mapped the entire space just by following the gradient flow of the heat equation.

This is the power of Physics-Informed Machine Learning. We can price high-dimensional exotics faster than traditional solvers because the neural network becomes a closed-form analytical function.

---

**[SCENE 11: 3D SURFACE VANISHES. THE EQUATION V = MAX(S-K, 0) APPEARS. IT MORPHS INTO V = MAX(K-S, 0) AS A QUESTION MARK GLOWS.]**

**(Pacing: Challenging, setting up the next step)**

But right now, this model only knows how to price a European Call option. Why?

Because we forced the terminal boundary condition to equal the Max of S minus K, or zero. The PDE for a Call and a Put option is exactly the same. The only thing that changes is the boundary.

Here is your challenge for Module 2.

Go into the Colab notebook linked below. Scroll to Step 1, and change the terminal boundary condition to represent a European **Put** option.

You don't need to touch the physics loss. You don't need to change the neural network architecture. Just change the boundary rule, run the training loop again, and watch how the exact same PDE forces the neural network to grow an entirely different mathematical surface.

In Module 3, we are going to break the dimensional barrier. We will take this exact SciML concept and use Deep BSDEs to price a basket of 100 correlated assets—a feat that is mathematically impossible for traditional grid-solvers.

Until then, keep your activations smooth, and I'll see you in the next frame.
# Recording Script: Module 1 – The Neural Taylor Series

## Scene 1: Introduction to Smoothness
> **Visual:** PURE DARKNESS. A FAINT GRID FADES IN. A BRIGHT WHITE LINE SNAPS INTO A 45-DEGREE "HOCKEY STICK" PAYOFF.
> **Direction:** *Pacing: Slow, deliberate, setting the historical stage*

In mathematics, we have a deep obsession with smoothness.

For centuries, if you wanted to understand a complex, twisting curve, you relied on the ultimate tool of mathematical approximation: the Taylor Series.

---

## Scene 2: The Taylor Series Philosophy
> **Visual:** A SMOOTH SINE WAVE APPEARS. A POLYNOMIAL CURVE WRAPS AROUND IT TIGHTLY.

The philosophy behind a Taylor Series is beautiful: if you know everything about a single point—its value, its slope, its acceleration, its infinite layers of derivatives—you can predict what the rest of the function looks like anywhere else. It treats a function like a lineage of DNA.

But in 1973, when Fischer Black and Myron Scholes set out to solve the option pricing problem, financial mathematics ran headfirst into a wall.

Finance doesn't like smooth curves. Finance likes boundaries.

---

## Scene 3: The Financial Kink
> **Visual:** CAMERA PANS TO THE HOCKEY STICK GRAPH. STOCK PRICE IS NEON GREEN, CONTRACT VALUE IS BRIGHT BLUE.
> **Direction:** *Pacing: slightly faster, highlighting the conflict*

Look at this payoff. This is a European Call Option at expiration. If the stock price stays below the strike price, the option is worth exactly zero. The moment it crosses that threshold, it gains value dollar-for-dollar.

Mathematically, this point right here—the strike price—is a catastrophe. It is a sharp, non-differentiable corner. A kink.

If you try to run a Taylor Series at this exact corner, the math shatters. The first derivative jumps instantly from zero to one. The second derivative—what quants call Gamma—explodes into infinity.

For decades, numerical finance had to work around this kink. We built rigid grids, sliced time into thousands of steps, and ran heavy Monte Carlo simulations, consuming massive computational power just to smooth out these corners.

> **Direction:** *Pacing: A brief pause. Lower pitch, signaling a paradigm shift.*

But what if we didn't have to build a grid? What if we could use an entirely different kind of mathematical engine? One that doesn't look at a single point's derivatives, but instead molds itself to the entire space all at once.

Today, we build our very first Scientific Machine Learning model. We are going to see exactly how a neural network leverages the Universal Approximation Theorem to learn the Black-Scholes surface—kinks, corners, and all—from scratch.

---

## Scene 4: The Option Surface (3D)
> **Visual:** 3D COORDINATE SYSTEM. A BLUE HOCKEY STICK SITS AT T=0. IT PULLS BACK IN TIME, MELTING INTO A SMOOTH HILL.
> **Direction:** *Pacing: Instructional and geometric*

To understand how a neural network solves this, we have to stop looking at flat 2D payoff charts and step into the third dimension. This is the Option Surface.

At the very end of time—when time to maturity equals zero—the option value must equal that sharp hockey stick. But watch what happens as we move backward in time.

The moment you add even a fraction of a second of time, uncertainty enters the room. Volatility blurs the corner. The sharp kink melts into a smooth curve. This entire 3D landscape is governed by the Black-Scholes formula.

Now, let’s bring in our neural network.

---

## Scene 5: The Elastic Sheet
> **Visual:** A WRINKLED, FLAT ORANGE SHEET APPEARS, CUTTING RANDOMLY THROUGH THE 3D SPACE.

Before training, a neural network is nothing more than a random guess.

In traditional machine learning, we treat this network as a black box. But geometrically, this network is an elastic sheet. The weights control the slope of the sheet; the biases control where it folds.

According to the Universal Approximation Theorem, if our network has enough hidden units and a non-linear activation function, it can deform, stretch, and bend itself to match any continuous surface to arbitrary precision.

---

## Scene 6: Training the Network
> **Visual:** THE ORANGE SHEET MORPHS AND STRETCHES OVER 100 FRAMES, PERFECTLY BLANKETING THE BLUE BLACK-SCHOLES SURFACE.

Watch what happens during training. The optimization algorithm pulls and pins the edges of our orange sheet to the boundary conditions, and then smooths out the center until the orange sheet perfectly blankets the true financial surface.

---

## Scene 7: Structural Blueprint
> **Visual:** CUT TO A DIGITAL WHITEBOARD. HAND-DRAWN SKETCH OF A NEURAL NETWORK APPEARS.
> **Direction:** *Pacing: Conversational, like a peer at a whiteboard*

Before we write a single line of Python, let’s lay out our structural blueprint. We aren’t building a generic model to predict stock prices tomorrow. We are building a functional engine.

Our input vector has two continuous dimensions: the current Stock Price $S$, and the remaining Time to Maturity $t$. These two numbers flow into a Multi-Layer Perceptron.

Inside the hidden layers, the network calculates combinations of these variables and passes them through an activation function. For SciML, our choice of activation function is critical.

If we use a standard neural network activation like ReLU, our surface will be made of flat, jagged facets. The first derivative will be choppy, and the second derivative—our Gamma—will be zero everywhere.

To preserve the laws of financial derivatives, we must use a smooth activation function like $\tanh$ or $\text{SiLU}$. This ensures that our learned surface is infinitely differentiable, allowing us to compute exact market Greeks later on.

Now, let’s jump into Google Colab and engineer this engine from scratch.

---

## Scene 8: Engineering Pipeline
> **Visual:** SPLIT SCREEN. MANIM 3D SURFACE ON LEFT. GOOGLE COLAB ON RIGHT.
> **Direction:** *Pacing: Instructional, guiding through the logic without reading every line of code*

First, we need an Oracle—a source of ground truth to train our elastic sheet. We'll generate a synthetic market of ten thousand option prices using the exact Black-Scholes analytical formula.

Next, we design the continuous neural surface. Notice our architecture. We stack linear layers, but in between each one, we specifically call `nn.Tanh()`. This is what guarantees our surface remains smooth and continuous.

Finally, we set up our engineering pipeline. We pass our stock prices and times into the network, calculate the Mean Squared Error against our Oracle, and let the Adam optimizer update the weights.

Let's run the training loop and watch the function space map itself out.

---

## Scene 9: Results and Challenge
> **Visual:** CODE FINISHES. VALIDATION CURVE PLOT APPEARS, SHOWING THE NN PERFECTLY OVERLAPPING THE TRUE BLACK-SCHOLES PRICE.
> **Direction:** *Pacing: Satisfied, conclusive, then shifting to a challenge*

Let’s look at our results.

Look at how cleanly the curves align. The orange neural network has tracked the true analytical solution perfectly, completely ignoring the challenge that the zero-boundary kink usually poses to traditional mathematical methods.

But this brings up our ultimate challenge.

We chose the Tanh activation function because it is smooth and infinitely differentiable. What happens if we look underneath the hood at the derivatives? What if we calculate Gamma—the second derivative of our option price with respect to the stock price?

---

## Scene 10: Homework and Outro
> **Visual:** PRESENTER ON CAMERA OR A SLOW PAN OF THE FINAL DASHBOARD.

Here is your homework challenge for this module. In the description below, you will find the link to this exact Google Colab notebook.

Open it up, go to Step 2, and change the activation function from `nn.Tanh()` to `nn.ReLU()`. Run the training pipeline again, check the resulting validation graph, and see what happens to the smoothness of the surface. Hint: Try to take a derivative of a jagged facet.

In the next video, we are going to remove the reliance on training data altogether. We will see what happens when we stop showing the network the answers, and instead teach it to read the laws of financial physics directly through Physics-Informed Neural Networks.
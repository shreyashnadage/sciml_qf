# ==============================================================================
# MANIM SCRIPT: MODULE 2 - THE PHYSICS OF NO-ARBITRAGE (PINNs)
# Run with: manim -pql scenes.py <SceneName>
# ==============================================================================

from manim import *
import numpy as np

# Global Color Palette for consistency across the series
C_SPOT = "#00FF00"    # Lime Green (S)
C_TIME = "#800080"    # Purple (t)
C_VAL  = "#0000FF"    # Bright Blue (V)
C_HEAT = "#FFA500"    # Neon Orange (Model/Heat)
C_GRAD = "#FF0000"    # Crimson Red (Gradients)

class Scene1_EmptyRoom(ThreeDScene):
    def construct(self):
        # [VOICEOVER]: In our last video, we proved that a neural network can learn 
        # the exact shape of a financial derivative.
        
        axes = ThreeDAxes(
            x_range=[50, 150, 20], 
            y_range=[0, 1, 0.2], 
            z_range=[0, 50, 10],
            axis_config={"include_numbers": True}
        ).shift(DOWN * 0.5)
        
        # Labels for 3D axes
        labels = axes.get_axis_labels(
            x_label=MathTex("S", color=C_SPOT), 
            y_label=MathTex("t", color=C_TIME), 
            z_label=MathTex("V", color=C_VAL)
        )
        
        self.set_camera_orientation(phi=65 * DEGREES, theta=35 * DEGREES)
        self.play(Create(axes), Write(labels))
        
        # Simulate a cloud of data points (Option Surface) - Optimized count
        dots = VGroup(*[
            Dot3D(axes.c2p(
                np.random.uniform(50, 150), 
                np.random.uniform(0, 1), 
                np.random.uniform(0, 50)
            ), color=C_VAL, radius=0.06) 
            for _ in range(80)
        ])
        
        # [VOICEOVER]: But we cheated. We generated ten thousand perfect data points 
        # using the analytical Black-Scholes formula, and we simply asked our 
        # network to memorize that shape.
        self.play(FadeIn(dots, lag_ratio=0.01), run_time=3)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(2)
        
        # [VOICEOVER]: In the real world of exotic derivatives, or 100-asset basket options, 
        # that perfect data doesn't exist. You cannot generate a billion data points to train 
        # a model because calculating even one point might take hours on a supercomputer.
        # So, we are faced with the 'Empty Room' problem. How do we teach a neural network 
        # to price a derivative when we have absolutely zero training data?
        
        self.stop_ambient_camera_rotation()
        # Optimized shockwave effect
        self.play(
            FadeOut(dots, shift=UP*1),
            run_time=1.5
        )
        
        # [VOICEOVER]: The answer lies in treating financial mathematics not as a statistical spreadsheet, 
        # but as the laws of physics. We don't need data if we know the rules of the game. 
        # And in quantitative finance, the ultimate rule is the law of No-Arbitrage.
        
        # Reset camera to 2D view for the equation
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=2)
        
        # [VOICEOVER]: This law is perfectly encapsulated in the Black-Scholes Partial Differential Equation.
        # Today, we are going to build a Physics-Informed Neural Network, or a PINN.
        
        pde = MathTex(
            r"\frac{\partial V}{\partial t}", r"+ \frac{1}{2}\sigma^2 S^2", r"\frac{\partial^2 V}{\partial S^2}", 
            r"+ rS \frac{\partial V}{\partial S} - rV = 0"
        ).scale(1.2)
        
        # [VOICEOVER]: We are going to lock our neural network in this empty room with nothing but this equation. 
        # It will have to teach itself how to price an option using only the laws of financial physics.
        self.play(Write(pde), run_time=3)
        self.wait(2)


class Scene2_GeometricIntuition(Scene):
    def construct(self):
        # [VOICEOVER]: To understand how a neural network can learn from an equation, 
        # we need to understand what this equation actually represents. At its core, 
        # the Black-Scholes PDE is a variation of the Heat Equation from classical physics.
        
        pde = MathTex(
            r"\frac{\partial V}{\partial t}", r"+ \frac{1}{2}\sigma^2 S^2", 
            r"\frac{\partial^2 V}{\partial S^2}", r"+ rS \frac{\partial V}{\partial S} - rV = 0"
        ).to_edge(UP)
        self.play(FadeIn(pde))

        # Define 2D axes for the "metal plate"
        axes = Axes(x_range=[50, 150, 20], y_range=[-10, 60, 10], axis_config={"color": GREY}).shift(DOWN*1)
        
        # [VOICEOVER]: Imagine a flat metal plate. If you take a blowtorch and heat a very specific, 
        # sharp jagged line into the center of it, that heat won't stay concentrated. 
        
        # Initial sharp payoff (Hockey stick)
        strike = 100
        payoff = axes.plot(lambda x: max(x - strike, 0), color=C_HEAT)
        self.play(Create(axes), Create(payoff))
        
        # [VOICEOVER]: Over time, it diffuses. It spreads out, seeking equilibrium.
        # In finance, that jagged blowtorch line is our terminal payoff—the hockey stick at expiration. 
        
        # Smooth out the payoff (Simulating heat diffusion / moving back in time)
        diffused_payoff_1 = axes.plot(lambda x: (x - strike) * 0.5 * (1 + np.tanh((x - strike)/10)) + 5, color=C_HEAT)
        diffused_payoff_2 = axes.plot(lambda x: (x - strike) * 0.5 * (1 + np.tanh((x - strike)/25)) + 15, color=C_HEAT)

        self.play(Transform(payoff, diffused_payoff_1), run_time=2)
        self.play(Transform(payoff, diffused_payoff_2), run_time=2)
        
        # [VOICEOVER]: And just like heat diffuses through metal over time, financial value diffuses 
        # through uncertainty. This term here, the second derivative of value with respect to stock price...
        
        # Highlight Gamma term
        gamma_term = pde[2]
        self.play(gamma_term.animate.set_color(C_GRAD))
        
        # [VOICEOVER]: ...our Gamma—acts as the diffusion operator. Volatility is the thermal 
        # conductivity of our market. 
        
        arrow = Arrow(start=gamma_term.get_bottom(), end=payoff.get_top(), color=C_GRAD)
        self.play(GrowArrow(arrow))
        self.wait(1)
        
        # [VOICEOVER]: If a financial surface obeys the law of no-arbitrage, all of these moving parts—time decay, 
        # diffusion, and drift—must perfectly balance out to equal zero everywhere in space and time. 
        # If they don't equal zero, an arbitrage opportunity exists.
        
        self.play(Indicate(pde[-1], scale_factor=1.5)) # Highlight the "= 0" part
        self.wait(2)


class Scene3_PINNArchitecture(Scene):
    def construct(self):
        # [VOICEOVER]: So, how do we enforce this law? We redefine our neural network's architecture. 
        # We still pass in our stock price and time, and it still outputs an option value.
        
        # Create NN Nodes
        node_S = Circle(radius=0.4, color=C_SPOT, fill_opacity=0.2).shift(LEFT*4, UP*1)
        node_t = Circle(radius=0.4, color=C_TIME, fill_opacity=0.2).shift(LEFT*4, DOWN*1)
        label_S = MathTex("S").move_to(node_S)
        label_t = MathTex("t").move_to(node_t)
        
        hidden_box = Rectangle(width=2, height=3, color=WHITE).shift(LEFT*1)
        label_hidden = Text("MLP", font_size=24).move_to(hidden_box)
        
        node_V = Circle(radius=0.4, color=C_VAL, fill_opacity=0.2).shift(RIGHT*2)
        label_V = MathTex("V").move_to(node_V)
        
        # Forward pass arrows
        f_arrows = VGroup(
            Arrow(node_S.get_right(), hidden_box.get_left(), color=WHITE),
            Arrow(node_t.get_right(), hidden_box.get_left(), color=WHITE),
            Arrow(hidden_box.get_right(), node_V.get_left(), color=WHITE)
        )
        
        self.play(FadeIn(node_S, label_S, node_t, label_t))
        self.play(Create(f_arrows), FadeIn(hidden_box, label_hidden))
        self.play(FadeIn(node_V, label_V))
        
        # [VOICEOVER]: But here is the brilliant twist. Because our neural network is made of smooth, 
        # differentiable functions like Tanh, we can use a mechanism called Automatic Differentiation.
        
        autograd_box = Rectangle(width=3, height=2, color=C_GRAD).shift(RIGHT*4, UP*2)
        label_autograd = Text("Autograd", font_size=24, color=C_GRAD).move_to(autograd_box)
        self.play(Create(autograd_box), Write(label_autograd))
        
        # [VOICEOVER]: We can ask PyTorch to exactly calculate the gradients of our network's output. 
        # We can extract the Delta and the Gamma directly from the network's weights.
        
        # Backward arrows
        b_arrow = CurvedArrow(node_V.get_top(), autograd_box.get_left(), angle=PI/2, color=C_GRAD)
        self.play(Create(b_arrow))
        
        greeks = MathTex(r"\frac{\partial V}{\partial t}, \frac{\partial V}{\partial S}, \frac{\partial^2 V}{\partial S^2}", color=C_GRAD)
        greeks.next_to(autograd_box, DOWN)
        self.play(Write(greeks))
        
        # [VOICEOVER]: We take those extracted gradients and plug them right back into the Black-Scholes equation. 
        # If the result is anything other than zero, we call that the 'Residual'.
        
        loss_box = Rectangle(width=4, height=1.5, color=C_HEAT).shift(RIGHT*3, DOWN*2)
        label_loss = MathTex(r"\text{Loss} = \text{MSE}(\mathcal{F}, 0)", color=C_HEAT).move_to(loss_box)
        
        loss_arrow = Arrow(greeks.get_bottom(), loss_box.get_top(), color=C_HEAT)
        
        self.play(Create(loss_box), Write(label_loss), GrowArrow(loss_arrow))
        
        # [VOICEOVER]: Our loss function is no longer the Mean Squared Error against data. 
        # Our loss function is the PDE Residual itself. We are penalizing the network for breaking 
        # the laws of physics. Let's write the code.
        self.wait(2)


class Scene4_DomainSampling(Scene):
    def construct(self):
        # [VOICEOVER]: Instead of data, we need to give the network a space to explore. 
        # We define a domain: stock prices from nearly zero to 150, and time from zero to 1 year.
        
        # Create domain box - centered and larger for intuition
        domain_axes = Axes(
            x_range=[0, 150, 25], 
            y_range=[0, 1, 0.2], 
            x_length=9, 
            y_length=5, 
            axis_config={"include_numbers": True, "color": GREY}
        ).shift(DOWN * 0.5)
        
        labels = domain_axes.get_axis_labels(
            x_label=MathTex("S", color=C_SPOT), 
            y_label=MathTex("t", color=C_TIME)
        )
        
        self.play(Create(domain_axes), Write(labels))
        
        # [VOICEOVER]: We randomly scatter thousands of coordinate points—called "collocation points"—
        # across this space. The network will evaluate the physics at these exact locations.
        
        # Scatter collocation points inside the domain
        dots = VGroup(*[
            Dot(domain_axes.c2p(np.random.uniform(10, 140), np.random.uniform(0.1, 0.9)), 
                radius=0.03, color=WHITE) 
            for _ in range(300)
        ])
        self.play(FadeIn(dots, lag_ratio=0.02), run_time=2)
        
        # [VOICEOVER]: Notice the 'requires_grad=True' flag. This is the secret to SciML. 
        # We are telling PyTorch: "Watch how the inputs change, because we are going to need their derivatives later."
        # We also define our boundary conditions—the walls of our room. 
        
        self.wait(1)
        
        # [VOICEOVER]: At expiration, the value must be the hockey stick payoff.
        
        # Highlight terminal boundary (t=1)
        terminal_line = Line(domain_axes.c2p(0, 1), domain_axes.c2p(150, 1), color=C_VAL, stroke_width=6)
        terminal_label = MathTex(r"V = \max(S-K, 0)", color=C_VAL).next_to(terminal_line, UP)
        
        self.play(Create(terminal_line))
        self.play(Write(terminal_label))
        # Keep this visible while Colab code is typed in the final video edit
        self.wait(3)


class Scene5_SanityCheckChallenge(ThreeDScene):
    def construct(self):
        # [VOICEOVER]: The loss drops. The network is learning the geometry of the market 
        # purely by staring at the PDE. Let's see what it built in the dark.
        
        axes = ThreeDAxes(
            x_range=[50, 150, 20], 
            y_range=[0, 1, 0.2], 
            z_range=[0, 50, 10],
            axis_config={"include_numbers": True}
        ).scale(0.8).shift(DOWN * 0.2)
        
        labels = axes.get_axis_labels(
            x_label=MathTex("S", color=C_SPOT), 
            y_label=MathTex("t", color=C_TIME), 
            z_label=MathTex("V", color=C_VAL)
        )
        
        self.set_camera_orientation(phi=45 * DEGREES, theta=35 * DEGREES)
        self.play(Create(axes), Write(labels))
        
        # Function for the surface (Mocking the BS surface for visualization)
        def bs_surface(u, v):
            S = u
            t = v
            # Dummy representation of the curved surface for visual effect
            val = max(S - 100, 0) * (1 - t) + (S * 0.5) * t 
            return axes.c2p(S, t, val)

        # [VOICEOVER]: Without a single piece of historical data, without a single Monte Carlo path, 
        # our neural network has discovered the exact Black-Scholes option surface. 
        
        # Render the PINN learned surface
        pinn_surface = Surface(
            bs_surface, u_range=[50, 150], v_range=[0, 1],
            resolution=(15, 15),
            fill_color=C_HEAT, fill_opacity=0.8, checkerboard_colors=[C_HEAT, C_HEAT]
        )
        self.play(Create(pinn_surface), run_time=3)
        
        # Full 360-degree rotation (2*PI radians)
        # Rate of 0.8 rad/s over 8 seconds covers ~2*PI
        self.begin_ambient_camera_rotation(rate=0.8)
        self.wait(8)
        self.stop_ambient_camera_rotation()
        
        # Transition to Challenge
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(pinn_surface), FadeOut(axes))
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES) # Reset to 2D
        
        # [VOICEOVER]: But right now, this model only knows how to price a European Call option. Why? 
        # Because we forced the terminal boundary condition to equal max(S-K, 0). 
        
        eq_call = MathTex(r"V = \max(", r"S - K", r", 0)").scale(2)
        self.play(Write(eq_call))
        
        # [VOICEOVER]: The PDE for a Call and a Put option is exactly the same. 
        # The only thing that changes is the boundary. Here is your challenge for Module 2. 
        # Go into the Colab notebook linked below. Scroll to Step 1, and change the terminal 
        # boundary condition to represent a European Put option.
        
        eq_put = MathTex(r"V = \max(", r"K - S", r", 0)").scale(2)
        
        # Animate the change from Call to Put boundary
        self.play(TransformMatchingTex(eq_call, eq_put), run_time=1.5)
        
        # [VOICEOVER]: You don't need to touch the physics loss. You don't need to change the architecture. 
        # Just change the boundary rule, run the training loop again, and watch how the exact same PDE 
        # forces the neural network to grow an entirely different mathematical surface.
        self.wait(3)

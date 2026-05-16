from manim import *
import numpy as np
from scipy.stats import norm

# Analytical Black-Scholes for the surface
def black_scholes_call(S, K, T, sigma, r):
    if T <= 1e-4: # Handle t=0
        return np.maximum(S - K, 0.0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

class OpeningPayoff(Scene):
    def construct(self):
        # 2D Payoff Chart
        axes = Axes(
            x_range=[0, 150, 10],
            y_range=[0, 60, 10],
            axis_config={"include_tip": True}
        )
        labels = axes.get_axis_labels(x_label="Stock Price (S)", y_label="Value (V)")
        
        K = 100
        payoff = axes.plot(
            lambda x: max(x - K, 0),
            color=BLUE,
            use_smoothing=False
        )
        
        payoff_label = Text("Call Option Payoff", font_size=24).next_to(payoff, UP, buff=0.5)
        
        self.play(Create(axes), Write(labels))
        self.play(Create(payoff), Write(payoff_label))
        self.wait(2)
        
        # Highlight the kink
        dot = Dot(axes.c2p(K, 0), color=RED)
        kink_text = Text("The Kink: Non-Differentiable", font_size=20, color=RED).next_to(dot, DR)
        self.play(FadeIn(dot), Write(kink_text))
        self.wait(2)

class OptionSurfaceWarp(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[50, 150, 20],
            y_range=[0, 2, 0.5],
            z_range=[0, 60, 20],
            x_length=6,
            y_length=6,
            z_length=4,
            axis_config={"include_tip": False}
        )
        
        # Labels
        x_label = axes.get_x_axis_label("S", edge=RIGHT, direction=RIGHT).set_color(GREEN)
        y_label = axes.get_y_axis_label("t", edge=UP, direction=UP).set_color(PURPLE)
        z_label = axes.get_z_axis_label("V", edge=OUT, direction=OUT).set_color(BLUE)

        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        self.add(axes, x_label, y_label, z_label)

        K = 100
        sigma = 0.2
        r = 0.05

        # Surface function
        surface = Surface(
            lambda s, t: axes.c2p(s, t, black_scholes_call(s, K, t, sigma, r)),
            u_range=[50, 150],
            v_range=[0.01, 2],
            resolution=(20, 20),
            should_make_jagged=False,
            fill_opacity=0.3,
            checkerboard_colors=[BLUE_D, BLUE_E]
        )
        
        # Terminal Payoff Curve
        payoff_curve = axes.plot_line_graph(
            x_values=np.linspace(50, 150, 100),
            y_values=np.zeros(100),
            z_values=[max(s - K, 0) for s in np.linspace(50, 150, 100)],
            line_color=BLUE,
            add_vertex_dots=False
        )

        self.play(Create(payoff_curve))
        self.wait(1)
        
        # Pulling backward in time
        self.play(Create(surface), run_time=3)
        self.wait(2)

class NeuralApproximator(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[50, 150, 20],
            y_range=[0, 2, 0.5],
            z_range=[0, 60, 20],
            x_length=6,
            y_length=6,
            z_length=4,
        )
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        self.add(axes)

        K = 100
        sigma = 0.2
        r = 0.05

        # Ground Truth Surface (Blue)
        true_surface = Surface(
            lambda s, t: axes.c2p(s, t, black_scholes_call(s, K, t, sigma, r)),
            u_range=[50, 150],
            v_range=[0.01, 2],
            fill_opacity=0.2,
            checkerboard_colors=[BLUE_D, BLUE_E]
        )
        
        # Initial Random Neural Surface (Wrinkled Orange)
        # Using a simple noise-like function to simulate "untrained" state
        def random_surface_func(s, t):
            val = 20 + 10 * np.sin(s/10) * np.cos(t*5)
            return axes.c2p(s, t, val)

        neural_surface = Surface(
            random_surface_func,
            u_range=[50, 150],
            v_range=[0.01, 2],
            fill_opacity=0.6,
            checkerboard_colors=[ORANGE, YELLOW]
        )

        self.add(true_surface)
        self.play(Create(neural_surface))
        self.wait(1)

        # Morphing animation
        self.play(
            neural_surface.animate.become(
                Surface(
                    lambda s, t: axes.c2p(s, t, black_scholes_call(s, K, t, sigma, r)),
                    u_range=[50, 150],
                    v_range=[0.01, 2],
                    fill_opacity=0.6,
                    checkerboard_colors=[ORANGE, YELLOW]
                )
            ),
            run_time=4
        )
        self.wait(2)

class ArchitectureWhiteboard(Scene):
    def construct(self):
        # Titles
        input_title = Text("Inputs", font_size=32).shift(UP * 3 + LEFT * 4)
        hidden_title = Text("Hidden Layers (MLP)", font_size=32).shift(UP * 3)
        output_title = Text("Output", font_size=32).shift(UP * 3 + RIGHT * 4)
        
        titles = VGroup(input_title, hidden_title, output_title)
        
        # Input Boxes
        s_box = VGroup(
            RoundedRectangle(corner_radius=0.1, height=1, width=2, color=GREEN),
            MathTex("S", color=GREEN)
        ).shift(LEFT * 4 + UP * 0.7)
        
        t_box = VGroup(
            RoundedRectangle(corner_radius=0.1, height=1, width=2, color=PURPLE),
            MathTex("t", color=PURPLE)
        ).shift(LEFT * 4 + DOWN * 0.7)
        
        # Hidden Layer Block
        mlp_box = VGroup(
            Rectangle(height=3, width=4, color=ORANGE),
            VGroup(
                Text("Linear + Tanh", font_size=24),
                MathTex(r"\sigma(\mathbf{W}\mathbf{x} + \mathbf{b})", font_size=36)
            ).arrange(DOWN, buff=0.3)
        ).shift(ORIGIN)
        
        # Output Box
        v_box = VGroup(
            RoundedRectangle(corner_radius=0.1, height=1, width=2, color=BLUE),
            MathTex("V", color=BLUE)
        ).shift(RIGHT * 4)
        
        # Arrows
        arrow_s = Arrow(s_box.get_right(), mlp_box.get_left() + UP * 0.5, buff=0.1, color=WHITE)
        arrow_t = Arrow(t_box.get_right(), mlp_box.get_left() + DOWN * 0.5, buff=0.1, color=WHITE)
        arrow_out = Arrow(mlp_box.get_right(), v_box.get_left(), buff=0.1, color=WHITE)
        
        # Animation sequence
        self.play(Write(titles))
        self.wait(1)
        
        self.play(Create(s_box), Create(t_box))
        self.play(Create(arrow_s), Create(arrow_t))
        self.wait(0.5)
        
        self.play(Create(mlp_box), run_time=2)
        self.wait(0.5)
        
        self.play(Create(arrow_out))
        self.play(Create(v_box))
        self.wait(3)

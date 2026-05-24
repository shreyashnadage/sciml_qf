from manim import *
import numpy as np
from scipy.stats import norm
import sys
import os
import json
from pathlib import Path
from manim_voiceover import VoiceoverScene

# Add the project root to sys.path so we can import qwen_voiceover
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from qwen_voiceover import QwenSpeechService

# Analytical Black-Scholes for the surface
def black_scholes_call(S, K, T, sigma, r):
    if T <= 1e-4: # Handle t=0
        return np.maximum(S - K, 0.0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

class SciMLScene(VoiceoverScene):
    def setup(self):
        config_path = os.environ.get("SCENE_CONFIG_PATH")
        if not config_path or not os.path.exists(config_path):
            self.scene_config = {
                "id": "manual",
                "voiceover": "This is fallback voiceover text.",
                "module_dir": str(Path(__file__).resolve().parents[2]),
                "global_config": {"voice": {"speaker": "Ryan"}}
            }
        else:
            with open(config_path, "r") as f:
                self.scene_config = json.load(f)
                
        media_dir = os.path.join(self.scene_config.get("module_dir", "."), "media", "voiceovers")
        speaker = self.scene_config.get("global_config", {}).get("voice", {}).get("speaker", "Ryan")
        self.set_speech_service(QwenSpeechService(speaker=speaker, cache_dir=media_dir))

    @property
    def voiceover_path(self):
        if "audio_path" in self.scene_config:
            return os.path.basename(self.scene_config["audio_path"])
        return None

class SciMLThreeDScene(ThreeDScene, VoiceoverScene):
    def setup(self):
        config_path = os.environ.get("SCENE_CONFIG_PATH")
        if not config_path or not os.path.exists(config_path):
            self.scene_config = {
                "id": "manual",
                "voiceover": "This is fallback voiceover text.",
                "module_dir": str(Path(__file__).resolve().parents[2]),
                "global_config": {"voice": {"speaker": "Ryan"}}
            }
        else:
            with open(config_path, "r") as f:
                self.scene_config = json.load(f)
                
        media_dir = os.path.join(self.scene_config.get("module_dir", "."), "media", "voiceovers")
        speaker = self.scene_config.get("global_config", {}).get("voice", {}).get("speaker", "Ryan")
        self.set_speech_service(QwenSpeechService(speaker=speaker, cache_dir=media_dir))

    @property
    def voiceover_path(self):
        if "audio_path" in self.scene_config:
            return os.path.basename(self.scene_config["audio_path"])
        return None

class OpeningPayoff(SciMLScene):
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
        
        scene_id = self.scene_config.get("id", "")
        
        if "intro_smoothness" in scene_id:
            with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
                self.play(Create(axes), Write(labels), run_time=tracker.duration * 0.4)
                self.play(Create(payoff), Write(payoff_label), run_time=tracker.duration * 0.4)
                self.wait(tracker.duration * 0.2)
                
        elif "financial_kink" in scene_id:
            dot = Dot(axes.c2p(K, 0), color=RED)
            kink_text = Text("The Kink: Non-Differentiable", font_size=20, color=RED).next_to(dot, DR)
            
            self.add(axes, labels, payoff, payoff_label)
            
            with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
                self.play(FadeIn(dot), Write(kink_text), run_time=tracker.duration * 0.3)
                self.wait(tracker.duration * 0.7)
        else:
            self.play(Create(axes), Write(labels))
            self.play(Create(payoff), Write(payoff_label))
            self.wait(2)
            dot = Dot(axes.c2p(K, 0), color=RED)
            kink_text = Text("The Kink: Non-Differentiable", font_size=20, color=RED).next_to(dot, DR)
            self.play(FadeIn(dot), Write(kink_text))
            self.wait(2)

class OptionSurfaceWarp(SciMLThreeDScene):
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

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            self.play(Create(payoff_curve), run_time=tracker.duration * 0.3)
            self.play(Create(surface), run_time=tracker.duration * 0.5)
            self.wait(tracker.duration * 0.2)

class NeuralApproximator(SciMLThreeDScene):
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
        scene_id = self.scene_config.get("id", "")
        
        if "elastic_sheet" in scene_id:
            with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
                self.play(Create(neural_surface), run_time=tracker.duration * 0.8)
                self.wait(tracker.duration * 0.2)
                
        elif "training_network" in scene_id:
            self.add(neural_surface)
            with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
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
                    run_time=tracker.duration * 0.8
                )
                self.wait(tracker.duration * 0.2)
        else:
            self.play(Create(neural_surface))
            self.wait(1)
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

class ArchitectureWhiteboard(SciMLScene):
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
        
        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Write(titles), run_time=d * 0.2)
            self.play(Create(s_box), Create(t_box), run_time=d * 0.2)
            self.play(Create(arrow_s), Create(arrow_t), run_time=d * 0.1)
            self.play(Create(mlp_box), run_time=d * 0.2)
            self.play(Create(arrow_out), Create(v_box), run_time=d * 0.2)
            self.wait(d * 0.1)

class TaylorApproximation(SciMLScene):
    def construct(self):
        # 1. Title / Header
        title = Text("Taylor Series Approximation of sin(x)", font_size=28).to_edge(UP)
        self.play(Write(title))
        
        # 2. Axes
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 2, 1],
            axis_config={"include_tip": True, "color": GRAY},
            x_length=8,
            y_length=4
        ).shift(DOWN * 0.5)
        
        labels = axes.get_axis_labels(x_label="x", y_label="f(x)")
        self.play(Create(axes), Write(labels))
        
        # 3. Target function: sin(x)
        target_curve = axes.plot(
            lambda x: np.sin(x),
            color=BLUE,
            x_range=[-4, 4]
        )
        target_label = MathTex(r"f(x) = \sin(x)", color=BLUE).next_to(axes.c2p(2, np.sin(2)), UR, buff=0.2)
        
        # 4. Taylor polynomials
        poly_1 = axes.plot(lambda x: x, color=RED, x_range=[-2, 2])
        label_1 = MathTex(r"P_1(x) = x", color=RED).to_corner(UL).shift(DOWN * 0.8)
        
        poly_3 = axes.plot(lambda x: x - (x**3)/6, color=ORANGE, x_range=[-3, 3])
        label_3 = MathTex(r"P_3(x) = x - \frac{x^3}{3!}", color=ORANGE).to_corner(UL).shift(DOWN * 0.8)
        
        poly_5 = axes.plot(lambda x: x - (x**3)/6 + (x**5)/120, color=YELLOW, x_range=[-3.5, 3.5])
        label_5 = MathTex(r"P_5(x) = x - \frac{x^3}{3!} + \frac{x^5}{5!}", color=YELLOW).to_corner(UL).shift(DOWN * 0.8)
        
        poly_7 = axes.plot(lambda x: x - (x**3)/6 + (x**5)/120 - (x**7)/5040, color=GREEN, x_range=[-4, 4])
        label_7 = MathTex(r"P_7(x) = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \frac{x^7}{7!}", color=GREEN).to_corner(UL).shift(DOWN * 0.8)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Create(target_curve), Write(target_label), run_time=d * 0.2)
            self.play(Create(poly_1), Write(label_1), run_time=d * 0.2)
            self.play(ReplacementTransform(poly_1, poly_3), ReplacementTransform(label_1, label_3), run_time=d * 0.2)
            self.play(ReplacementTransform(poly_3, poly_5), ReplacementTransform(label_3, label_5), run_time=d * 0.2)
            self.play(ReplacementTransform(poly_5, poly_7), ReplacementTransform(label_5, label_7), run_time=d * 0.2)




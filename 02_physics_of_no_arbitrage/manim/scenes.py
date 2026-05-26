from manim import *
import numpy as np
from scipy.stats import norm
import sys
import os
import json
from pathlib import Path
from manim_voiceover import VoiceoverScene
import torch

# Add the project root to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from qwen_voiceover import QwenSpeechService

# Helper for BS Surface
def bs_call(S, K, T, sigma, r):
    if T <= 1e-4: return np.maximum(S - K, 0.0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

# Base Classes per Rule.md
class SciMLScene(VoiceoverScene):
    def setup(self):
        config_path = os.environ.get("SCENE_CONFIG_PATH")
        if not config_path or not os.path.exists(config_path):
            self.scene_config = {"id": "manual", "voiceover": "Fallback text.", "module_dir": ".", "global_config": {"voice": {"speaker": "Ryan"}}}
        else:
            with open(config_path, "r") as f: self.scene_config = json.load(f)
        media_dir = os.path.join(self.scene_config.get("module_dir", "."), "media", "voiceovers")
        speaker = self.scene_config.get("global_config", {}).get("voice", {}).get("speaker", "Ryan")
        self.set_speech_service(QwenSpeechService(speaker=speaker, cache_dir=media_dir))
    @property
    def voiceover_path(self): return os.path.basename(self.scene_config["audio_path"]) if "audio_path" in self.scene_config else None

class SciMLThreeDScene(ThreeDScene, VoiceoverScene):
    def setup(self):
        config_path = os.environ.get("SCENE_CONFIG_PATH")
        if not config_path or not os.path.exists(config_path):
            self.scene_config = {"id": "manual", "voiceover": "Fallback text.", "module_dir": ".", "global_config": {"voice": {"speaker": "Ryan"}}}
        else:
            with open(config_path, "r") as f: self.scene_config = json.load(f)
        media_dir = os.path.join(self.scene_config.get("module_dir", "."), "media", "voiceovers")
        speaker = self.scene_config.get("global_config", {}).get("voice", {}).get("speaker", "Ryan")
        self.set_speech_service(QwenSpeechService(speaker=speaker, cache_dir=media_dir))
    @property
    def voiceover_path(self): return os.path.basename(self.scene_config["audio_path"]) if "audio_path" in self.scene_config else None


# ---------------------------------------------------------
# ACT 1: THE EMPTY ROOM (Squishing the Sheet)
# ---------------------------------------------------------
class EmptyRoom(SciMLThreeDScene):
    def construct(self):
        axes = ThreeDAxes(x_range=[50, 150, 20], y_range=[0, 1, 0.2], z_range=[0, 60, 20])
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        self.add(axes)

        true_surface = Surface(
            lambda s, t: axes.c2p(s, t, bs_call(s, 100, t, 0.2, 0.05)),
            u_range=[50, 150], v_range=[0.01, 1], fill_opacity=0.4, color=BLUE
        )
        self.add(true_surface)

        squish_tracker = ValueTracker(0)

        def get_squished_sheet():
            val = squish_tracker.get_value()
            return Surface(
                # Creates a wavy, distorted sheet that wiggles based on the tracker
                lambda s, t: axes.c2p(s, t, 15 + 10 * np.sin(s/10 + val) * np.cos(t*5 + val)),
                u_range=[50, 150], v_range=[0, 1], fill_opacity=0.8, checkerboard_colors=[ORANGE, YELLOW]
            )

        orange_sheet = always_redraw(get_squished_sheet)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.wait(d * 0.1)
            self.play(FadeOut(true_surface, shift=OUT), run_time=d * 0.2)
            self.add(orange_sheet)
            # Animate the squishing/searching behavior
            self.play(squish_tracker.animate.set_value(10), run_time=d * 0.6, rate_func=linear)
            self.wait(d * 0.1)


# ---------------------------------------------------------
# ACT 2: TIME EXPANSION (2D to 3D Melting)
# ---------------------------------------------------------
class TimeExpansion(SciMLThreeDScene):
    def construct(self):
        # FIX 1: Add zoom=0.8 to pull the camera back and give the scene "breathing room"
        #self.set_camera_orientation(phi=90 * DEGREES, theta=-90 * DEGREES, zoom=0.8)
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.8)
        
        # FIX 2: Slightly reduced z_length (from 5 to 4) for better aesthetic proportions
        axes = ThreeDAxes(
            x_range=[50, 150, 20], y_range=[0, 8, 1], z_range=[0, 60, 20],
            x_length=8, y_length=6, z_length=4
        )
        
        # Shift the entire axis down to perfectly center the [0, 60] volume in the frame
        axes.shift(DOWN * 3)
        
        # Add Neat Labels
        x_label = axes.get_x_axis_label(Tex("Stock Price ($S$)"))
        y_label = axes.get_y_axis_label(Tex("Time ($t$)"))
        z_label = axes.get_z_axis_label(Tex("Payoff ($V$)"))
        
        K = 100
        
        # The T=0 Payoff (Clean line, NO dots)
        payoff_2d = axes.plot_line_graph(
            x_values=np.linspace(50, 150, 100),
            y_values=np.zeros(100),
            z_values=[max(s - K, 0) for s in np.linspace(50, 150, 100)],
            line_color=BLUE, 
            stroke_width=6,
            add_vertex_dots=False
        )

        # FIX 2: Create text and explicitly lock it to the 2D camera frame overlay
        time_tracker = ValueTracker(0.0)
        time_text = Text("Time to Maturity (T): 0.0 Months", font_size=28).to_corner(UR)
        self.add_fixed_in_frame_mobjects(time_text)
        
        # Update the text smoothly without losing its 2D fixed status
        time_text.add_updater(
            lambda m: m.become(
                Text(f"Time to Maturity (T): {time_tracker.get_value():.1f} Months", font_size=28).to_corner(UR)
            )
        )

        def get_expanding_surface():
            t_max = max(time_tracker.get_value(), 0.01)
            return Surface(
                lambda s, t: axes.c2p(s, t, bs_call(s, K, t/8.0, 0.2, 0.05)), # Assuming bs_call is defined
                u_range=[50, 150], 
                v_range=[0.01, t_max],
                resolution=(16, 12), # Keep resolution low for smooth rendering
                fill_opacity=0.7, 
                checkerboard_colors=[BLUE_D, BLUE_E]
            )

        surface_3d = always_redraw(get_expanding_surface)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Step 1: Draw the 2D front view (X and Z axes only, plus the payoff and fixed timer)
            self.play(
                Create(axes.x_axis), Create(axes.z_axis), 
                Write(x_label), Write(z_label), 
                run_time=d * 0.15
            )
            self.play(Create(payoff_2d), run_time=d * 0.15)
            
            # Step 2: Tilt the camera to an isometric view
            self.move_camera(phi=70 * DEGREES, theta=-45 * DEGREES, run_time=d * 0.2)
            
            # Step 3: Animate the Time axis growing, its label appearing, and the surface expanding
            self.add(surface_3d)
            self.play(
                Create(axes.y_axis), 
                Write(y_label),
                time_tracker.animate.set_value(8.0), 
                run_time=d * 0.4, 
                rate_func=linear
            )
            self.wait(d * 0.1)


# ---------------------------------------------------------
# ACT 3: THE PDE SCALE
# ---------------------------------------------------------
class PDEScale(SciMLThreeDScene):
    def construct(self):
        # The PDE Legend pinned to screen
        pde_eq = MathTex(
            r"\frac{\partial V}{\partial t}", 
            r"+ \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2}", 
            r"+ rS \frac{\partial V}{\partial S}", 
            r"- rV = 0",
            font_size=40
        ).to_edge(UP)
        pde_eq[0].set_color(PURPLE) # Theta
        pde_eq[1].set_color(ORANGE) # Gamma
        pde_eq[2].set_color(GREEN)  # Delta
        pde_eq[3].set_color(BLUE)   # Risk-Free
        self.add_fixed_in_frame_mobjects(pde_eq)

        # 3D Setup with Zoom to avoid clipping
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=0.8)
        
        # Explicit bounds and steps to avoid too many ticks
        axes = ThreeDAxes(
            x_range=[50, 150, 20], y_range=[0, 1, 0.2], z_range=[0, 60, 20],
            x_length=8, y_length=6, z_length=4
        )
        axes.shift(DOWN * 1.2) # Centering it
        
        # Axes Labels
        x_label = axes.get_x_axis_label(Tex("Stock Price ($S$)"))
        y_label = axes.get_y_axis_label(Tex("Time ($t$)"))
        z_label = axes.get_z_axis_label(Tex("Payoff ($V$)"))
        
        surface = Surface(
            lambda s, t: axes.c2p(s, t, bs_call(s, 100, t, 0.2, 0.05)),
            u_range=[50, 150], v_range=[0.01, 1], fill_opacity=0.3, color=WHITE
        )
        self.add(axes, surface, x_label, y_label, z_label)

        # Arbitrary Point
        pt = axes.c2p(110, 0.5, bs_call(110, 100, 0.5, 0.2, 0.05))
        dot = Dot3D(pt, color=WHITE, radius=0.1)
        
        # 3D Vectors
        vec_theta = Arrow(pt, pt + np.array([0, 0, -2]), color=PURPLE, buff=0)
        vec_delta = Arrow(pt, pt + np.array([1, 0, 1]), color=GREEN, buff=0)
        vec_gamma = Arrow(pt, pt + np.array([-1, 1, 0]), color=ORANGE, buff=0)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Write(pde_eq), run_time=d * 0.1)
            
            # Zoom to point and extract vectors
            self.move_camera(frame_center=pt, zoom=1.2, added_anims=[FadeIn(dot)], run_time=d * 0.1)
            
            # Show the arbitrary point clearly with a slight rotation of the camera during vector growth
            self.move_camera(
                phi=65 * DEGREES, 
                theta=-30 * DEGREES, 
                run_time=d * 0.2,
                added_anims=[GrowArrow(vec_theta), GrowArrow(vec_delta), GrowArrow(vec_gamma)]
            )
            
            # Transition to 2D Stack (Fade 3D, Reset Camera to 2D)
            self.move_camera(
                frame_center=ORIGIN,
                phi=0,
                theta=-90 * DEGREES,
                zoom=1.0,
                added_anims=[
                    FadeOut(surface), FadeOut(axes), FadeOut(dot),
                    FadeOut(x_label), FadeOut(y_label), FadeOut(z_label)
                ],
                run_time=d * 0.2
            )

            # Create three 2D arrows that will stack on top of each other
            arrow_theta = Arrow(start=[-3, -1.5, 0], end=[-3, -0.5, 0], color=PURPLE, stroke_width=4, buff=0)
            arrow_delta = Arrow(start=[-3, -0.5, 0], end=[-3, 0.5, 0], color=GREEN, stroke_width=4, buff=0)
            arrow_gamma = Arrow(start=[-3, 0.5, 0], end=[-3, 1.5, 0], color=ORANGE, stroke_width=4, buff=0)
            
            # Group them
            stacked_system = VGroup(arrow_theta, arrow_delta, arrow_gamma)
            
            # We will fix them in frame after the transition so they don't appear prematurely
            self.play(
                ReplacementTransform(vec_theta, arrow_theta),
                ReplacementTransform(vec_delta, arrow_delta),
                ReplacementTransform(vec_gamma, arrow_gamma),
                run_time=d * 0.1
            )
            self.add_fixed_in_frame_mobjects(arrow_theta, arrow_delta, arrow_gamma)
            
            # Equal Sign
            equal_sign = MathTex("=", font_size=48).move_to([-1.5, -0.5, 0])
            self.add_fixed_in_frame_mobjects(equal_sign)
            
            # Blue vector rV on the right
            vec_rv = Arrow(start=[0, -1.5, 0], end=[0, 1.0, 0], color=BLUE, stroke_width=4, buff=0)
            self.add_fixed_in_frame_mobjects(vec_rv)
            
            self.play(
                Write(equal_sign),
                GrowArrow(vec_rv),
                run_time=d * 0.1
            )
            
            # Squish down
            self.play(
                stacked_system.animate.stretch_to_fit_height(1.8, about_edge=DOWN),
                run_time=d * 0.08,
                rate_func=rate_functions.ease_out_quad
            )
            # Expand up
            self.play(
                stacked_system.animate.stretch_to_fit_height(3.2, about_edge=DOWN),
                run_time=d * 0.08,
                rate_func=rate_functions.ease_out_quad
            )
            # Settle to match rV (exactly 2.5 height)
            self.play(
                stacked_system.animate.stretch_to_fit_height(2.5, about_edge=DOWN),
                run_time=d * 0.08,
                rate_func=rate_functions.ease_out_quad
            )
            self.wait(d * 0.06)


# ---------------------------------------------------------
# ACT 4: THE HINGE (ReLU vs Tanh Matrices)
# ---------------------------------------------------------
class Activations(SciMLScene):
    def construct(self):
        # Neural Network Equation Matrix
        eq_relu = MathTex(
            r"y = \text{ReLU} \left( \begin{bmatrix} w_1 & w_2 & w_3 \end{bmatrix} \begin{bmatrix} \frac{\partial V}{\partial t} \\ \frac{\partial V}{\partial S} \\ \frac{\partial^2 V}{\partial S^2} \end{bmatrix} + b \right)",
            font_size=40
        ).to_edge(UP)
        
        eq_tanh = MathTex(
            r"y = \tanh \left( \begin{bmatrix} w_1 & w_2 & w_3 \end{bmatrix} \begin{bmatrix} \frac{\partial V}{\partial t} \\ \frac{\partial V}{\partial S} \\ \frac{\partial^2 V}{\partial S^2} \end{bmatrix} + b \right)",
            font_size=40
        ).to_edge(UP)

        # Graph Setup
        axes = Axes(x_range=[-3, 3, 1], y_range=[-1, 3, 1], x_length=8, y_length=4).shift(DOWN)
        
        # ReLU Components
        curve_relu = axes.plot(lambda x: max(x, 0), color=RED, stroke_width=6)
        dot_relu = Dot(color=WHITE)
        tangent_relu = Line(LEFT, RIGHT, color=YELLOW, stroke_width=4)
        
        x_tracker = ValueTracker(-2.5)
        angle_tracker = ValueTracker(0.0)

        def update_dot_relu(d):
            x = x_tracker.get_value()
            d.move_to(axes.c2p(x, max(x, 0)))

        def update_tangent_relu(t):
            x = x_tracker.get_value()
            t.move_to(axes.c2p(x, max(x, 0)))
            if abs(x) < 1e-4:
                t.set_angle(angle_tracker.get_value())
            elif x > 0:
                t.set_angle(np.arctan(1))
            else:
                t.set_angle(0)

        # Tanh Components
        curve_tanh = axes.plot(lambda x: np.tanh(x) + 1, color=GREEN, stroke_width=6)
        
        def update_dot_tanh(d):
            x = x_tracker.get_value()
            d.move_to(axes.c2p(x, np.tanh(x) + 1))

        def update_tangent_tanh(t):
            x = x_tracker.get_value()
            t.move_to(axes.c2p(x, np.tanh(x) + 1))
            t.set_angle(np.arctan(1 - np.tanh(x)**2))

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Write(eq_relu), Create(axes), run_time=d * 0.08)
            self.play(Create(curve_relu), run_time=d * 0.05)
            
            # Roll ReLU (Snaps at 0)
            dot_relu.add_updater(update_dot_relu)
            tangent_relu.add_updater(update_tangent_relu)
            self.add(dot_relu, tangent_relu)
            
            # Roll to the kink (0.0)
            self.play(x_tracker.animate.set_value(0.0), run_time=d * 0.08, rate_func=linear)
            
            # The Panic: Wobbling wildly between flat (0) and angled (PI/4)
            for _ in range(2):
                self.play(angle_tracker.animate.set_value(PI/4), run_time=d * 0.05, rate_func=there_and_back)
                self.play(angle_tracker.animate.set_value(0), run_time=d * 0.05, rate_func=there_and_back)
                
            # Disappear (Fade Out tangent line and dot)
            dot_relu.clear_updaters()
            tangent_relu.clear_updaters()
            self.play(FadeOut(tangent_relu), FadeOut(dot_relu), run_time=d * 0.05)
            
            # Swap to Tanh
            self.play(
                TransformMatchingTex(eq_relu, eq_tanh), 
                Transform(curve_relu, curve_tanh),
                x_tracker.animate.set_value(-2.5),
                run_time=d * 0.08
            )
            
            # Roll Tanh (Smooth)
            dot_relu.add_updater(update_dot_tanh)
            tangent_relu.add_updater(update_tangent_tanh)
            self.play(
                FadeIn(dot_relu), FadeIn(tangent_relu),
                x_tracker.animate.set_value(2.5),
                run_time=d * 0.12,
                rate_func=linear
            )


# ---------------------------------------------------------
# ACT 5: Code Walkthrough
# ---------------------------------------------------------
class CodeWalkthroughScene(SciMLScene):
    def construct(self):
        scene_id = self.scene_config.get("id", "")
        
        # Read the config values or use fallbacks
        code_file = self.scene_config.get("code_file", "code/pinn_black_scholes.py")
        code_range = self.scene_config.get("code_range", [50, 75])
        highlights = self.scene_config.get("highlights", [
            {"lines": [53, 56], "pause": 2.0},
            {"lines": [60, 68], "pause": 2.0},
            {"lines": [71, 74], "pause": 2.0}
        ])
        voiceover_text = self.scene_config.get("voiceover", "Let us look at the Python script. First... the empty room. We scatter random coordinate points across space and time. Next... the physics loss. We ask the network for a prediction, then extract the Delta and Gamma directly from the network weights using PyTorch. Finally... we plug those derivatives into our P D E scale. We penalize the network until that scale balances to zero.")
        
        # Get absolute path to original file
        module_dir = self.scene_config.get("module_dir", ".")
        original_file_path = os.path.join(module_dir, code_file)
        
        # Create temp file path
        temp_code_dir = Path("media")
        temp_code_dir.mkdir(parents=True, exist_ok=True)
        temp_file_path = temp_code_dir / "temp_cleaned_code.py"
        
        # Read original code
        try:
            with open(original_file_path, "r") as f:
                lines = f.readlines()
        except Exception as e:
            # Fallback if code file doesn't exist during manual test
            lines = [f"# Line {i}\n" for i in range(1, 100)]
            
        start_line = code_range[0] - 1
        end_line = code_range[1]
        target_lines = lines[start_line:end_line]
        
        # Sanitize
        cleaned_lines = []
        for line in target_lines:
            if line.strip() == "":
                cleaned_lines.append(" \n")
            else:
                cleaned_lines.append(line.replace("\t", "    "))
                
        # Write sanitized code
        with open(temp_file_path, "w") as f:
            f.writelines(cleaned_lines)
            
        # Instantiate Code
        rendered_code = Code(
            code_file=str(temp_file_path),
            line_numbers_from=code_range[0],
            tab_width=4,
            background="window",
            language="python",
            formatter_style="monokai"
        )
        
        # Scale and position
        code_window = rendered_code.scale(0.8).move_to(ORIGIN)
        
        if "scene_5" in scene_id:
            with self.voiceover(text=voiceover_text, path=self.voiceover_path) as tracker:
                total_duration = tracker.duration
                
                # Fade in code window
                self.play(FadeIn(code_window), run_time=total_duration * 0.1)
                
                # Active highlight object
                active_rect = None
                
                # We have 3 highlights. Let's allocate time proportionally.
                # Total proportional time left: 0.85 of total_duration
                # We will split it into 3 segments: 0.25, 0.25, 0.25, and a final wait/fadeout of 0.15
                segment_durations = [0.25, 0.25, 0.25]
                
                for idx, hl in enumerate(highlights):
                    hl_start = hl["lines"][0] - code_range[0]
                    hl_end = hl["lines"][-1] - code_range[0]
                    
                    if hl_start >= 0 and hl_end < len(code_window.code_lines):
                        # Combined line numbers and code text VGroup for highlight
                        line_nums = code_window.line_numbers[hl_start : hl_end + 1]
                        line_texts = code_window.code_lines[hl_start : hl_end + 1]
                        lines_to_highlight = VGroup(line_nums, line_texts)
                        
                        new_rect = SurroundingRectangle(
                            lines_to_highlight,
                            color=YELLOW, buff=0.1, fill_opacity=0.2
                        )
                        
                        run_time = total_duration * segment_durations[idx]
                        
                        if active_rect is None:
                            self.play(Create(new_rect), run_time=run_time * 0.3)
                            active_rect = new_rect
                            self.wait(run_time * 0.7)
                        else:
                            self.play(Transform(active_rect, new_rect), run_time=run_time * 0.3)
                            self.wait(run_time * 0.7)
                            
                # Fade out everything
                fade_out_anims = [FadeOut(code_window)]
                if active_rect is not None:
                    fade_out_anims.append(FadeOut(active_rect))
                self.play(*fade_out_anims, run_time=total_duration * 0.15)
        else:
            # Fallback block for manual testing
            self.play(FadeIn(code_window), run_time=1.0)
            active_rect = None
            for hl in highlights:
                hl_start = hl["lines"][0] - code_range[0]
                hl_end = hl["lines"][-1] - code_range[0]
                if hl_start >= 0 and hl_end < len(code_window.code_lines):
                    line_nums = code_window.line_numbers[hl_start : hl_end + 1]
                    line_texts = code_window.code_lines[hl_start : hl_end + 1]
                    lines_to_highlight = VGroup(line_nums, line_texts)
                    new_rect = SurroundingRectangle(
                        lines_to_highlight,
                        color=YELLOW, buff=0.1, fill_opacity=0.2
                    )
                    if active_rect is None:
                        self.play(Create(new_rect), run_time=0.5)
                        active_rect = new_rect
                    else:
                        self.play(Transform(active_rect, new_rect), run_time=0.5)
                    self.wait(2.0)
            
            fade_out_anims = [FadeOut(code_window)]
            if active_rect is not None:
                fade_out_anims.append(FadeOut(active_rect))
            self.play(*fade_out_anims, run_time=1.0)


# ---------------------------------------------------------
# ACT 6: PINN Discovery
# ---------------------------------------------------------
class PINN(torch.nn.Module):
    def __init__(self):
        super(PINN, self).__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(2, 64),
            torch.nn.Tanh(),
            torch.nn.Linear(64, 64),
            torch.nn.Tanh(),
            torch.nn.Linear(64, 64),
            torch.nn.Tanh(),
            torch.nn.Linear(64, 1)
        )

    def forward(self, S, t):
        inputs = torch.cat([S, t], dim=1)
        return self.net(inputs)

class PINNDiscoveryScene(SciMLThreeDScene):
    def construct(self):
        # 3D Setup with Zoom to avoid clipping
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.8)
        
        # Explicit bounds and steps to avoid too many ticks
        axes = ThreeDAxes(
            x_range=[50, 150, 20], y_range=[0, 1, 0.2], z_range=[0, 60, 20],
            x_length=8, y_length=6, z_length=4
        )
        axes.shift(DOWN * 1.5) # Centering it
        
        # Axes Labels
        x_label = axes.get_x_axis_label(Tex("Stock Price ($S$)"))
        y_label = axes.get_y_axis_label(Tex("Time ($t$)"))
        z_label = axes.get_z_axis_label(Tex("Payoff ($V$)"))
        
        K = 100
        # True Analytical Surface (Blue, semi-transparent)
        true_surface = Surface(
            lambda s, t: axes.c2p(s, t, bs_call(s, K, t, 0.2, 0.05)),
            u_range=[50, 150], v_range=[0.01, 1],
            resolution=(16, 12),
            fill_opacity=0.3, color=BLUE
        )
        
        # Untrained Neural Surface (Flat orange sheet, hovering at Z=45)
        untrained_surface = Surface(
            lambda s, t: axes.c2p(s, t, 45),
            u_range=[50, 150], v_range=[0.01, 1],
            resolution=(16, 12),
            fill_opacity=0.8, checkerboard_colors=[ORANGE, YELLOW]
        )
        
        # Instantiate and load model
        model = PINN()
        module_dir = self.scene_config.get("module_dir", ".")
        model_path = os.path.join(module_dir, "code", "pinn_model.pth")
        
        try:
            if os.path.exists(model_path):
                model.load_state_dict(torch.load(model_path))
            model.eval()
        except Exception as e:
            print(f"Error loading model weights: {e}")
            
        def pinn_predict(s, t):
            S_tensor = torch.tensor([[s]], dtype=torch.float32)
            t_tensor = torch.tensor([[t]], dtype=torch.float32)
            with torch.no_grad():
                val = model(S_tensor, t_tensor).item()
            return val
            
        # Trained Neural Surface (getting predicted values from the trained NN)
        trained_surface = Surface(
            lambda s, t: axes.c2p(s, t, pinn_predict(s, t)),
            u_range=[50, 150], v_range=[0.01, 1],
            resolution=(16, 12),
            fill_opacity=0.8, checkerboard_colors=[ORANGE, YELLOW]
        )
        
        self.add(axes, x_label, y_label, z_label, true_surface)
        
        # Legend (Fixed in frame)
        legend_blue = Text("Blue Surface = True Math", font_size=24, color=BLUE).to_corner(UL)
        legend_orange = Text("Orange Sheet = PINN Model", font_size=24, color=ORANGE).next_to(legend_blue, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(legend_blue, legend_orange)
        
        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Start ambient rotation
            self.begin_ambient_camera_rotation(rate=0.08)
            
            # Fade in the flat orange sheet representing the untrained network
            self.play(FadeIn(untrained_surface), run_time=d * 0.2)
            self.wait(d * 0.1)
            
            # Morph the flat orange sheet into the solved surface (optimizer in action)
            self.play(
                Transform(untrained_surface, trained_surface),
                run_time=d * 0.5,
                rate_func=smooth
            )
            
            self.wait(d * 0.2)
            self.stop_ambient_camera_rotation()
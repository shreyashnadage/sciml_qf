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


# HELPER FUNCTIONS

def black_scholes_call(S, K, T, sigma, r):
    if T <= 1e-4: # Handle t=0 (The Kink)
        return np.maximum(S - K, 0.0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


# BASE CLASSES (from template)

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


# SCENE 1A: The "No-Formula" Objective (The Hook & Goal)

class ObjectiveHook(SciMLThreeDScene):
    def construct(self):
        # 3D Option Surface (Rotating in background)
        axes = ThreeDAxes(x_range=[50, 150, 20], y_range=[0, 1, 0.2], z_range=[0, 60, 20])
        surface = Surface(
            lambda s, t: axes.c2p(s, t, black_scholes_call(s, 100, t, 0.2, 0.05)),
            u_range=[50, 150], v_range=[0.01, 1], fill_opacity=0.3, checkerboard_colors=[BLUE_D, BLUE_E]
        ).shift(RIGHT * 3)
        
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        self.add(surface)
        self.begin_ambient_camera_rotation(rate=0.1)

        # BS Formula (Fixed in frame)
        bs_formula = MathTex(
            r"V = S \Phi(d_1) - K e^{-rt} \Phi(d_2)", font_size=48
        ).to_edge(LEFT).shift(UP)
        self.add_fixed_in_frame_mobjects(bs_formula)

        # Blank Neural Network Architecture
        nn_group = VGroup(
            Circle(radius=0.3, color=WHITE, fill_opacity=0.2),
            Circle(radius=0.3, color=WHITE, fill_opacity=0.2),
            Circle(radius=0.3, color=WHITE, fill_opacity=0.2)
        ).arrange(DOWN, buff=0.5).to_edge(LEFT).shift(DOWN)
        self.add_fixed_in_frame_mobjects(nn_group)
        nn_group.set_opacity(0)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            self.play(Write(bs_formula), run_time=tracker.duration * 0.2)
            self.wait(tracker.duration * 0.2)
            
            # Formula dissolves into dust (Scale up and fade out)
            self.play(bs_formula.animate.scale(1.5).set_opacity(0), run_time=tracker.duration * 0.2)
            
            # NN Fades in and pulses
            self.play(nn_group.animate.set_opacity(1), run_time=tracker.duration * 0.2)
            self.play(Indicate(nn_group, color=ORANGE, scale_factor=1.2), run_time=tracker.duration * 0.2)

        self.stop_ambient_camera_rotation()


# SCENE 1B: The Smooth Taylor Wrap

class TaylorWrap(SciMLScene):
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

# SCENE 1C: The Tangent Panic (The Financial Conflict)

class TangentPanic(MovingCameraScene, VoiceoverScene):
    def setup(self):
        # Explicit setup for VoiceoverScene combined with MovingCameraScene
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

    def construct(self):
        K = 100
        axes = Axes(x_range=[80, 120, 10], y_range=[0, 20, 5], x_length=8, y_length=5)
        
        # Hockey Stick Payoff
        payoff = axes.plot(lambda x: max(x - K, 0), color=BLUE)
        kink_point = Dot(axes.c2p(K, 0), color=RED)
        
        # Tangent Line mechanism
        angle_tracker = ValueTracker(0) # 0 is flat, PI/4 is 45 degrees
        
        def get_tangent_line():
            angle = angle_tracker.get_value()
            line = Line(LEFT * 2, RIGHT * 2, color=WHITE)
            line.rotate(angle)
            line.move_to(kink_point.get_center())
            return line

        tangent_line = always_redraw(get_tangent_line)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Create(axes), Create(payoff), run_time=d * 0.2)
            
            # Camera aggressively zooms in on the kink
            self.play(
                self.camera.frame.animate.scale(0.4).move_to(kink_point.get_center() + UP*0.5),
                FadeIn(kink_point),
                run_time=d * 0.2
            )
            
            self.add(tangent_line)
            
            # The Panic: Wobbling wildly between flat (0) and angled (PI/4)
            for _ in range(6):
                self.play(angle_tracker.animate.set_value(PI/4), run_time=d * 0.05, rate_func=there_and_back)
                self.play(angle_tracker.animate.set_value(0), run_time=d * 0.05, rate_func=there_and_back)
            
            self.wait(d * 0.1)


# SCENE 2A: The Melting Surface

class MeltingSurface(SciMLThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[50, 150, 20], y_range=[0, 1, 0.2], z_range=[0, 60, 20],
            x_length=7, y_length=7, z_length=4
        )
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES) # Start 2D Top-Down
        
        K = 100
        # The 2D Hockey Stick at t=0
        hockey_stick = axes.plot(lambda s: max(s - K, 0), color=BLUE).shift(OUT * axes.c2p(0,0,0)[2])
        self.add(axes, hockey_stick)

        time_tracker = ValueTracker(0.01)

        def get_melting_surface():
            t_val = time_tracker.get_value()
            return Surface(
                lambda s, t: axes.c2p(s, t, black_scholes_call(s, K, t, 0.2, 0.05)),
                u_range=[50, 150], v_range=[0.01, max(t_val, 0.02)],
                fill_opacity=0.8, color=BLUE
            )

        melting_surface = always_redraw(get_melting_surface)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            # Orbit to 3D
            self.move_camera(phi=75 * DEGREES, theta=-45 * DEGREES, run_time=d * 0.3)
            
            # Sweep forward across the time axis (melting)
            self.add(melting_surface)
            self.play(time_tracker.animate.set_value(1.0), run_time=d * 0.6, rate_func=linear)
            self.wait(d * 0.1)


# SCENE 2B: Enter the Elastic Sheet

class ElasticSheet(SciMLThreeDScene):
    def construct(self):
        axes = ThreeDAxes(x_range=[50, 150, 20], y_range=[0, 1, 0.2], z_range=[0, 60, 20])
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        
        # True Surface
        true_surface = Surface(
            lambda s, t: axes.c2p(s, t, black_scholes_call(s, 100, t, 0.2, 0.05)),
            u_range=[50, 150], v_range=[0.01, 1], fill_opacity=0.3, color=BLUE
        )
        self.add(axes, true_surface)

        # Legend
        legend_blue = Text("Blue Surface = True Math", font_size=24, color=BLUE).to_corner(UL)
        legend_orange = Text("Orange Sheet = Neural Network", font_size=24, color=ORANGE).next_to(legend_blue, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(legend_blue, legend_orange)

        # Flat Orange Grid hovering above
        flat_sheet = Surface(
            lambda s, t: axes.c2p(s, t, 45), # Hovering at Z=45
            u_range=[50, 150], v_range=[0, 1], fill_opacity=0.8, checkerboard_colors=[ORANGE, YELLOW]
        )

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            self.play(Write(legend_blue), run_time=tracker.duration * 0.2)
            
            # Sheet drops down from above
            flat_sheet.shift(OUT * 2)
            self.play(
                flat_sheet.animate.shift(IN * 2), 
                Write(legend_orange), 
                run_time=tracker.duration * 0.6
            )
            self.wait(tracker.duration * 0.2)


# SCENE 3A: The Blueprint and The Heat

class ArchitectureBlueprint(SciMLScene):
    def construct(self):
        # Nodes
        node_s = Circle(radius=0.5, color=GREEN, fill_opacity=0.2).shift(LEFT * 4 + UP * 2)
        label_s = Text("Stock Price", font_size=24).next_to(node_s, LEFT)
        
        node_t = Circle(radius=0.5, color=PURPLE, fill_opacity=0.2).shift(LEFT * 4)
        label_t = Text("Time", font_size=24).next_to(node_t, LEFT)
        
        node_vol = Circle(radius=0.5, color=RED, fill_opacity=0.2).shift(LEFT * 4 + DOWN * 2)
        label_vol = Text("Volatility", font_size=24, color=RED).next_to(node_vol, LEFT)

        # Central Box
        sheet_box = RoundedRectangle(corner_radius=0.2, height=3, width=4, color=ORANGE).shift(RIGHT * 2)
        sheet_label = Text("Neural Sheet", font_size=32).move_to(sheet_box)

        # Connections
        lines = VGroup(
            Line(node_s.get_right(), sheet_box.get_left() + UP * 1, color=WHITE),
            Line(node_t.get_right(), sheet_box.get_left(), color=WHITE),
            Line(node_vol.get_right(), sheet_box.get_left() + DOWN * 1, color=WHITE)
        )

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(FadeIn(node_s, label_s, node_t, label_t), run_time=d * 0.2)
            self.play(Create(sheet_box), Write(sheet_label), run_time=d * 0.2)
            self.play(Create(lines[0:2]), run_time=d * 0.1)
            
            # Explicitly highlight volatility (The Heat)
            self.play(FadeIn(node_vol, label_vol), Create(lines[2]), run_time=d * 0.2)
            self.play(Indicate(node_vol, color=YELLOW, scale_factor=1.3), run_time=d * 0.2)
            self.wait(d * 0.1)


# SCENE 3B: The Hinge Demonstration

class HingeDemonstration(SciMLScene):
    def construct(self):
        axes = Axes(x_range=[-3, 3, 1], y_range=[-1, 3, 1], x_length=6, y_length=4)
        
        # Flat line (the stiff board)
        flat_line = axes.plot(lambda x: 0, color=ORANGE, stroke_width=8)
        
        # ReLU Fold (Harsh, jagged crease)
        relu_fold = axes.plot(lambda x: max(x, 0), color=ORANGE, stroke_width=8)
        cross = Cross(scale_factor=0.5).next_to(axes.c2p(0, 0), UP, buff=0.5)
        
        # Tanh Fold (Smooth bending metal)
        tanh_fold = axes.plot(lambda x: np.tanh(x) + 1, color=ORANGE, stroke_width=8) # Offset for visibility
        check = MathTex(r"\checkmark", color=GREEN).scale(2).next_to(axes.c2p(0, 1), UP, buff=0.5)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Create(axes), Create(flat_line), run_time=d * 0.1)
            
            # Show ReLU harsh fold
            self.play(Transform(flat_line, relu_fold), run_time=d * 0.2)
            self.play(Create(cross), run_time=d * 0.1)
            self.wait(d * 0.1)
            
            # Show Tanh smooth fold
            self.play(FadeOut(cross), Transform(flat_line, tanh_fold), run_time=d * 0.3)
            self.play(FadeIn(check), run_time=d * 0.1)
            self.wait(d * 0.1)


# SCENE 4A: Code Walkthrough (Manim Code Object)

class CodeWalkthrough(SciMLScene):
    def construct(self):
        code_str = """
# 1. THE ORACLE (Generating True Data)
V_true = black_scholes_call(S, K, T, sigma, r)

# 2. THE ELASTIC SHEET (Neural Architecture)
class OptionSurfaceNet(nn.Module):
    def __init__(self):
        self.sheet = nn.Sequential(
            nn.Linear(2, 64),
            nn.Tanh(),        # The smooth hinge!
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )

# 3. THE TRAINING LOOP (Pinning it Down)
optimizer = optim.Adam(model.parameters())
for epoch in range(1000):
    predictions = model(X_train)
    loss = criterion(predictions, V_true)
    loss.backward()
    optimizer.step()
"""
        # Step 1: Prepare Code Window
        temp_code_dir = Path("media")
        temp_code_dir.mkdir(parents=True, exist_ok=True)
        temp_file_path = temp_code_dir / "temp_cleaned_code.py"

        # Sanitize empty lines/tabs
        cleaned_lines = []
        for line in code_str.splitlines():
            if line.strip() == "":
                cleaned_lines.append(" \n")
            else:
                cleaned_lines.append(line.replace("\t", "    ") + "\n")

        with open(temp_file_path, "w") as f:
            f.writelines(cleaned_lines)

        rendered_code = Code(
            code_file=str(temp_file_path),
            language="python",
            background="window"
        )

        # Center the code window and scale it so it fills the screen cleanly
        rendered_code.scale(0.85).move_to(ORIGIN)

        # Start standard animation sequence with voiceover mapping
        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            self.play(FadeIn(rendered_code), run_time=tracker.duration * 0.1)

            # === START WALKTHROUGH ===

            # 1. ORACLE: Extract correct lines (1 through 2) and target with new Rect
            oracle_lines = VGroup(*rendered_code.code_lines[1:3])
            highlight = SurroundingRectangle(oracle_lines, color=YELLOW, fill_opacity=0.2)

            self.play(
                Create(highlight),
                run_time=tracker.duration * 0.25
            )
            self.wait(tracker.duration * 0.05)

            # 2. ARCHITECTURE: Extract architecture (focus Tanh smooth hinge)
            arch_lines = VGroup(*rendered_code.code_lines[5:14]) # Entire Net
            
            # Transform the OLD highlight rect into a NEW correctly sized rect
            new_rect = SurroundingRectangle(arch_lines, color=YELLOW, fill_opacity=0.2)

            self.play(
                Transform(highlight, new_rect),
                run_time=tracker.duration * 0.25
            )
            # Indicate special sub-element (Tanh hinge)
            self.play(Indicate(VGroup(*rendered_code.code_lines[9]), color=ORANGE, scale_factor=1.1), run_time=tracker.duration * 0.05)
            self.wait(tracker.duration * 0.05)

            # 3. TRAINING LOOP: Extract lines and target
            loop_lines = VGroup(*rendered_code.code_lines[15:22])
            
            # TransformOLD rect into NEW accurately sized rect
            final_rect = SurroundingRectangle(loop_lines, color=YELLOW, fill_opacity=0.2)

            self.play(
                Transform(highlight, final_rect),
                run_time=tracker.duration * 0.2
            )
            # Indicate critical loss function update
            self.play(Indicate(rendered_code.code_lines[20], color=RED, scale_factor=1.1), run_time=tracker.duration * 0.05)
            self.wait(tracker.duration * 0.05)

            # Final Clean up if needed, or hold scene.
            self.play(FadeOut(highlight))
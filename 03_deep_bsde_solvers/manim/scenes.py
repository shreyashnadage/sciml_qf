from manim import *
import numpy as np
import sys
import os
import json
from pathlib import Path
from manim_voiceover import VoiceoverScene

# Add the project root to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from qwen_voiceover import QwenSpeechService

# ==============================================================================
# BASE CLASSES (Handling TTS and Configs)
# ==============================================================================
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


# ==============================================================================
# SCENE 0: The Prologue (Dimensional Wall)
# ==============================================================================
class Prologue(SciMLThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=0.9)
        
        # 1D Line
        line = Line(LEFT*2, RIGHT*2, color=BLUE)
        dots_1d = VGroup(*[Dot(point=line.point_from_proportion(p), color=WHITE, radius=0.08) for p in np.linspace(0, 1, 5)])
        
        # 2D Grid
        grid_2d = NumberPlane(x_range=[-2, 2, 1], y_range=[-2, 2, 1], x_length=4, y_length=4, background_line_style={"stroke_color": BLUE})
        
        # 3D Cube
        cube = Cube(side_length=4, fill_opacity=0, stroke_color=BLUE, stroke_width=2)
        
        # UI Elements
        counter = Tex("$10^d$", font_size=72, color=RED).to_edge(UP)
        curse_text = Text("The Curse of Dimensionality", font_size=36, color=WHITE).next_to(counter, DOWN)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # 1D -> 2D -> 3D Extrusion
            self.play(Create(line), FadeIn(dots_1d), run_time=d * 0.1)
            self.play(ReplacementTransform(line, grid_2d), FadeOut(dots_1d), run_time=d * 0.15)
            self.play(ReplacementTransform(grid_2d, cube), run_time=d * 0.15)
            
            # The Explosion of dimensions
            self.add_fixed_in_frame_mobjects(counter, curse_text)
            self.play(FadeIn(counter), run_time=d * 0.1)
            
            # Animate the counter 10^3 -> 10^50
            for val in [10, 20, 50]:
                new_counter = Tex(f"$10^{{{val}}}$ Grid Nodes", font_size=72, color=RED).to_edge(UP)
                self.play(Transform(counter, new_counter), run_time=d * 0.1)
            
            self.play(FadeIn(curse_text), cube.animate.set_color(RED).set_stroke(width=6), run_time=d * 0.1)
            
            # Shatter and clear
            self.move_camera(
                phi=0 * DEGREES, theta=-90 * DEGREES, # Back to 2D
                run_time=d * 0.1,
                added_anims=[FadeOut(cube, scale=1.5), FadeOut(counter), FadeOut(curse_text)]
            )


# ==============================================================================
# SCENE 1: 1D Monte Carlo
# ==============================================================================
class MonteCarlo1D(SciMLScene):
    def construct(self):
        # Ticks every 0.2 for time, every 20 for stock
        axes = Axes(x_range=[0, 1, 0.2], y_range=[60, 140, 20], x_length=8, y_length=5)
        axes.add_coordinates()
        x_label = axes.get_x_axis_label(Tex("Time ($t$)"))
        y_label = axes.get_y_axis_label(Tex("Stock Price ($S_t$)"))
        
        K = 100
        strike_line = DashedVMobject(axes.plot(lambda x: K, color=YELLOW))
        strike_label = Tex("Strike ($K$)", color=YELLOW, font_size=28).next_to(strike_line, RIGHT)

        # Generate GBM Paths
        np.random.seed(42)
        paths = []
        path_ends = []
        for _ in range(8):
            dt = 0.02
            S = [100]
            for _ in range(50):
                S.append(S[-1] * np.exp((0.05 - 0.5*0.04)*dt + 0.2*np.sqrt(dt)*np.random.randn()))
            paths.append(axes.plot_line_graph(x_values=np.linspace(0, 1, 51), y_values=S, line_color=BLUE_E, add_vertex_dots=False))
            path_ends.append(S[-1])

        eq = MathTex(r"V_0 = e^{-rT} \mathbb{E}[\max(S_T - K, 0)]", font_size=40).to_edge(UP)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Create(axes), Write(x_label), Write(y_label), run_time=d * 0.1)
            self.play(Create(strike_line), FadeIn(strike_label), run_time=d * 0.1)
            
            # Animate paths
            self.play(*[Create(p) for p in paths], run_time=d * 0.4)
            
            # Highlight ITM paths (ending > K)
            itm_anims = []
            for p, end_val in zip(paths, path_ends):
                if end_val > K:
                    itm_anims.append(p.animate.set_color(GREEN).set_stroke(width=4))
            
            self.play(*itm_anims, run_time=d * 0.2)
            self.play(Write(eq), run_time=d * 0.2)


# ==============================================================================
# SCENE 2: Basket Option (2D to 3D)
# ==============================================================================
class BasketOption3D(SciMLThreeDScene):
    def construct(self):
        # Start in 2D perspective (looking straight down Z axis)
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=0.8)
        
        # X=Time, Y=Stock1, Z=Stock2
        axes = ThreeDAxes(
            x_range=[0, 1, 0.2], y_range=[60, 140, 20], z_range=[60, 140, 20],
            x_length=7, y_length=5, z_length=5
        ).shift(DOWN * 2)
        axes.add_coordinates()
        
        x_label = axes.get_x_axis_label(Tex("Time ($t$)"))
        y_label = axes.get_y_axis_label(Tex("Stock 1"))
        z_label = axes.get_z_axis_label(Tex("Stock 2"))

        # ITM Boundary at t=1: S1 * S2 = K^2 -> Y * Z = 10000
        boundary_curve = ParametricFunction(
            lambda v: axes.c2p(1.0, v, 10000/v),
            t_range=[71.4, 140], color=YELLOW, stroke_width=4
        )
        # Translucent ITM plane area
        itm_surface = Surface(
            lambda u, v: axes.c2p(1.0, u, v),
            u_range=[71.4, 140], v_range=[71.4, 140],
            fill_opacity=0.3, color=GREEN
        )

        eq = MathTex(r"V_0 = e^{-rT} \mathbb{E}[\max(\sqrt{S_1 S_2} - K, 0)]", font_size=36).to_corner(UR)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Create(axes.x_axis), Create(axes.y_axis), Write(x_label), Write(y_label), run_time=d * 0.1)
            
            # Rotate to 3D and reveal Z axis (Stock 2)
            self.move_camera(phi=75 * DEGREES, theta=-45 * DEGREES, run_time=d * 0.2, added_anims=[Create(axes.z_axis), Write(z_label)])
            
            # Draw 3D paths
            np.random.seed(1)
            path_curves = []
            for _ in range(4):
                t = np.linspace(0, 1, 20)
                y = 100 + np.cumsum(np.random.randn(20)*5)
                z = 100 + np.cumsum(np.random.randn(20)*5)
                pts = [axes.c2p(t[i], y[i], z[i]) for i in range(20)]
                curve = VMobject().set_points_smoothly(pts).set_color(BLUE)
                path_curves.append(curve)

            self.play(*[Create(p) for p in path_curves], run_time=d * 0.3)
            
            # Reveal Terminal Boundary
            self.play(Create(boundary_curve), run_time=d * 0.1)
            self.play(FadeIn(itm_surface), run_time=d * 0.1)
            
            self.add_fixed_in_frame_mobjects(eq)
            self.play(Write(eq), run_time=d * 0.2)


# ==============================================================================
# SCENE 3: Bump and Revalue (The Curse)
# ==============================================================================
class BumpAndRevalue(SciMLScene):
    def construct(self):
        # The Delta Equation
        eq = MathTex(
            r"\Delta = \frac{", r"V(S + \epsilon)", r" - ", r"V(S - \epsilon)", r"}{2\epsilon}",
            font_size=48, arg_separator=""
        ).to_edge(UP)
        eq[1].set_color(GREEN) # V(S + \epsilon)
        eq[3].set_color(RED)   # V(S - \epsilon)

        # 1D Axes
        axes = Axes(x_range=[0, 1, 0.2], y_range=[70, 130, 20], x_length=6, y_length=3).shift(DOWN*0.5)
        axes.add_coordinates()
        x_label = axes.get_x_axis_label(Tex("Time ($t$)"))
        y_label = axes.get_y_axis_label(Tex("Stock Price ($S_t$)"))
        
        # Generate GBM Paths
        np.random.seed(42)
        base_paths = []
        up_paths = []
        dn_paths = []
        
        for _ in range(4):
            dt = 0.02
            shocks = np.random.randn(50)
            
            # Base path (starts at 100)
            S_base = [100]
            for i in range(50):
                S_base.append(S_base[-1] * np.exp((0.05 - 0.5*0.04)*dt + 0.2*np.sqrt(dt)*shocks[i]))
            base_p = axes.plot_line_graph(x_values=np.linspace(0, 1, 51), y_values=S_base, line_color=WHITE, add_vertex_dots=False)
            base_p["line_graph"].set_fill(opacity=0)
            base_p["line_graph"].set_stroke(opacity=0.3)
            base_paths.append(base_p)
            
            # Up-shocked path (starts at 105)
            S_up = [105]
            for i in range(50):
                S_up.append(S_up[-1] * np.exp((0.05 - 0.5*0.04)*dt + 0.2*np.sqrt(dt)*shocks[i]))
            up_p = axes.plot_line_graph(x_values=np.linspace(0, 1, 51), y_values=S_up, line_color=GREEN, add_vertex_dots=False)
            up_paths.append(up_p)
            
            # Down-shocked path (starts at 95)
            S_dn = [95]
            for i in range(50):
                S_dn.append(S_dn[-1] * np.exp((0.05 - 0.5*0.04)*dt + 0.2*np.sqrt(dt)*shocks[i]))
            dn_p = axes.plot_line_graph(x_values=np.linspace(0, 1, 51), y_values=S_dn, line_color=RED, add_vertex_dots=False)
            dn_paths.append(dn_p)

        box_1d = VGroup(Rectangle(width=3, height=0.6, color=BLUE, fill_opacity=0.2), Text("1 Asset = 2 Sims", font_size=20)).next_to(axes, DOWN)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Write(eq), run_time=d * 0.15)
            self.play(Create(axes), Write(x_label), Write(y_label), run_time=d * 0.15)
            self.play(*[Create(bp) for bp in base_paths], run_time=d * 0.3)
            
            # Bumps
            self.play(*[Create(up) for up in up_paths], run_time=d * 0.3)
            self.play(*[Create(dn) for dn in dn_paths], run_time=d * 0.3)
            self.play(FadeIn(box_1d), run_time=d * 0.1)
            
            # Scale to 50 assets (Grid Multiplier)
            self.play(
                FadeOut(axes), 
                *[FadeOut(bp) for bp in base_paths],
                *[FadeOut(up) for up in up_paths],
                *[FadeOut(dn) for dn in dn_paths],
                run_time=d * 0.1
            )
            
            grid = VGroup(*[box_1d.copy().scale(0.3) for _ in range(100)])
            grid.arrange_in_grid(rows=10, cols=10, buff=0.1).move_to(ORIGIN).shift(DOWN*0.5)
            
            self.play(Transform(box_1d, grid), run_time=d * 0.15)
            
            final_text = Text("Total Paths: 1,000,000+", color=RED, font_size=40).move_to(ORIGIN)
            self.play(FadeIn(final_text, scale=1.5), grid.animate.set_opacity(0.1), run_time=d * 0.1)


# ==============================================================================
# SCENE 4: The Hedging Game (Deep BSDE)
# ==============================================================================
class HedgingGame(SciMLScene):
    def construct(self):
        # Top: Market Axes (X=Time, Y=Stock)
        ax_top = Axes(x_range=[0, 1, 0.2], y_range=[80, 120, 10], x_length=7, y_length=2.5).to_edge(UP)
        ax_top.add_coordinates()
        lbl_top_x = ax_top.get_x_axis_label(Tex("Time ($t$)"))
        lbl_top_y = ax_top.get_y_axis_label(Tex("Stock Price ($S_t$)"))
        
        # Bottom: Wealth Ledger (X=None, Y=Wealth)
        ax_bot = Axes(x_range=[0, 1, 1], y_range=[0, 20, 5], x_length=2, y_length=2.5).to_edge(DOWN).shift(LEFT*2.5)
        ax_bot.add_coordinates()
        lbl_bot = ax_bot.get_y_axis_label(Tex("Wealth ($Y_t$)"))
        
        # Center UI
        nn_icon = VGroup(Circle(radius=0.4, color=BLUE, fill_opacity=0.2), Text("NN", font_size=20)).move_to(RIGHT*2)
        y0_label = Text("Initial Cash (Y_0)", font_size=24, color=YELLOW).next_to(nn_icon, UP)
        
        # Equations
        bsde_eq = MathTex(r"dY_t = rY_t dt + Z_t dW_t", font_size=36).to_corner(DR)
        z_def = Tex(r"$Z = \sigma S \Delta$", font_size=28, color=GREEN).next_to(bsde_eq, UP)

        # Dynamic Trackers
        t_tracker = ValueTracker(0.0)
        wealth_tracker = ValueTracker(10.0) # Starts at Y_0 = 10
        
        # Live Bar and Counter
        bar = always_redraw(lambda: Rectangle(
            width=0.8, height=ax_bot.c2p(0, wealth_tracker.get_value())[1] - ax_bot.c2p(0, 0)[1],
            color=GREEN, fill_opacity=0.7
        ).move_to(ax_bot.c2p(0.5, wealth_tracker.get_value()/2)))
        
        counter = always_redraw(lambda: Text(f"${wealth_tracker.get_value():.2f}", font_size=24, color=GREEN)
                                .next_to(bar, UP, buff=0.1))

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Setup split screen
            self.play(Create(ax_top), Write(lbl_top_x), Write(lbl_top_y), Create(ax_bot), Write(lbl_bot), run_time=d * 0.15)
            
            # Init Y_0
            self.play(FadeIn(nn_icon), Write(y0_label), run_time=d * 0.1)
            self.play(FadeIn(bar), FadeIn(counter), run_time=d * 0.1)
            
            # Equation Reveal
            self.play(Write(bsde_eq), Write(z_def), run_time=d * 0.15)
            
            # Gameplay (Draw stock path, randomly update wealth)
            stock_pts = [ax_top.c2p(0, 100), ax_top.c2p(0.3, 110), ax_top.c2p(0.6, 95), ax_top.c2p(1.0, 115)]
            path = VMobject().set_points_smoothly(stock_pts).set_color(BLUE)
            
            # We animate the line drawing and wealth fluctuating
            self.play(
                Create(path),
                wealth_tracker.animate(rate_func=there_and_back).set_value(16.0),
                run_time=d * 0.3
            )
            # End Wealth stabilizes at $11.50
            self.play(wealth_tracker.animate.set_value(11.50), run_time=d*0.05)
            
            # The Miss
            target_val = 15.0
            target_line = DashedVMobject(ax_bot.plot(lambda x: target_val, color=WHITE))
            target_txt = Text("True Payoff: $15.00", font_size=20).next_to(target_line, RIGHT)
            
            self.play(Create(target_line), FadeIn(target_txt), run_time=d * 0.05)
            
            # Red Bracket
            bracket = BraceBetweenPoints(ax_bot.c2p(1, 11.5), ax_bot.c2p(1, 15), color=RED, direction=RIGHT)
            loss_txt = bracket.get_text("Loss").set_color(RED)
            
            self.play(Create(bracket), FadeIn(loss_txt), bar.animate.set_color(RED), counter.animate.set_color(RED), run_time=d * 0.1)


# ==============================================================================
# SCENE 5: The Architecture (Backprop)
# ==============================================================================
class Architecture(SciMLScene):
    def construct(self):
        # Timeline
        timeline = Line(LEFT*4, RIGHT*4, color=WHITE).shift(DOWN)
        nodes = VGroup(*[Circle(radius=0.3, color=BLUE, fill_opacity=0.2).move_to(timeline.point_from_proportion(p)) for p in np.linspace(0, 1, 5)])
        labels = VGroup(*[MathTex(f"t_{i}" if i<4 else "T").next_to(nodes[i], DOWN) for i in range(5)])
        
        # Walls and Dials
        payoff_wall = Rectangle(width=0.2, height=2, color=WHITE, fill_opacity=1).next_to(nodes[-1], RIGHT, buff=1)
        wall_txt = Text("True Payoff", font_size=20).next_to(payoff_wall, UP)
        
        dial_w = VGroup(Circle(radius=0.4, color=YELLOW), Text("Weights", font_size=16)).next_to(nodes[0], UP*3 + LEFT)
        dial_y0 = VGroup(Circle(radius=0.4, color=GREEN), Text("Y_0 Dial", font_size=16)).next_to(nodes[0], UP*3 + RIGHT)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Unroll time
            self.play(Create(timeline), FadeIn(nodes), FadeIn(labels), run_time=d * 0.15)
            
            # Forward Pass (Blue pulse)
            pulse = Dot(color=BLUE).move_to(nodes[0].get_center())
            self.play(FadeIn(pulse), run_time=d * 0.05)
            
            for i in range(4):
                self.play(pulse.animate.move_to(nodes[i+1].get_center()), run_time=d * 0.1)
                
            # Collision and Loss
            self.play(FadeIn(payoff_wall), FadeIn(wall_txt), pulse.animate.move_to(payoff_wall.get_left()), run_time=d * 0.1)
            loss_box = Text("Loss (MSE)", color=RED, font_size=24).next_to(pulse, UP)
            self.play(FadeIn(loss_box), pulse.animate.set_color(RED).scale(1.5), run_time=d * 0.1)
            
            # Backward Pass (Red pulse)
            self.play(FadeIn(dial_w), FadeIn(dial_y0), run_time=d * 0.05)
            
            for i in range(4, -1, -1):
                self.play(pulse.animate.move_to(nodes[i].get_center()), run_time=d * 0.05)
                
            # Update Dials
            self.play(
                Rotate(dial_w[0], angle=PI/2), 
                Rotate(dial_y0[0], angle=-PI/2), 
                pulse.animate.set_opacity(0),
                run_time=d * 0.1
            )


# ==============================================================================
# SCENE 6: Code Walkthrough
# ==============================================================================
class CodeWalkthroughScene(SciMLScene):
    def construct(self):
        scene_id = self.scene_config.get("id", "")
        
        # Read the config values or use fallbacks
        code_file = self.scene_config.get("code_file", "code/deep_bsde_solver.py")
        code_range = self.scene_config.get("code_range", [15, 95])
        highlights = self.scene_config.get("highlights", [])
        voiceover_text = self.scene_config.get("voiceover", "Fallback voiceover.")
        
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
        except Exception:
            lines = [f"# Line {i}\n" for i in range(1, 150)]
            
        start_line = code_range[0] - 1
        end_line = code_range[1]
        target_lines = lines[start_line:end_line]
        
        # Sanitize
        cleaned_lines = []
        for line in target_lines:
            cleaned_lines.append(line.replace("\t", "    "))
                
        # Write sanitized code
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)
            
        # Instantiate Code - using disable_ligatures=False to prevent Pango index out of range crash on Windows
        rendered_code = Code(
            code_file=str(temp_file_path),
            line_numbers_from=code_range[0],
            tab_width=4,
            background="window",
            language="python",
            formatter_style="monokai",
            paragraph_config={"disable_ligatures": False}
        )
        
        # Scale and position
        code_window = rendered_code.scale(0.65).move_to(ORIGIN)
        
        if "scene_6" in scene_id:
            with self.voiceover(text=voiceover_text, path=self.voiceover_path) as tracker:
                total_duration = tracker.duration
                
                # Fade in code window fully opaque
                self.play(FadeIn(code_window), run_time=total_duration * 0.1)
                
                # We have highlights. Let's allocate time proportionally.
                num_hl = max(len(highlights), 1)
                segment_durations = [0.80 / num_hl] * num_hl
                
                for idx, hl in enumerate(highlights):
                    # Parse search_string or fallback to lines
                    hl_start = 0
                    hl_end = 0
                    if "search_string" in hl:
                        search_str = hl["search_string"]
                        for i, line in enumerate(target_lines):
                            if search_str in line:
                                hl_start = i
                                hl_end = i + hl.get("lines_count", 1) - 1
                                break
                    else:
                        hl_start = hl["lines"][0] - code_range[0]
                        hl_end = hl["lines"][-1] - code_range[0]
                        
                    if hl_start >= 0 and hl_end < len(code_window.code_lines):
                        # Center of the active lines
                        active_group = VGroup(*[code_window.code_lines[i] for i in range(hl_start, min(hl_end + 1, len(code_window.code_lines)))])
                        shift_y = -active_group.get_center()[1]
                        shift_vector = np.array([0, shift_y, 0])
                        
                        # Create target state
                        target_window = code_window.copy()
                        target_window.shift(shift_vector)
                        
                        # Apply opacity changes to target
                        for i, line in enumerate(target_window.code_lines):
                            target_opacity = 1.0 if (hl_start <= i <= hl_end) else 0.2
                            line.set_opacity(target_opacity)
                        for i, num in enumerate(target_window.line_numbers):
                            target_opacity = 1.0 if (hl_start <= i <= hl_end) else 0.2
                            num.set_opacity(target_opacity)
                            
                        run_time = total_duration * segment_durations[idx]
                        
                        self.play(
                            Transform(code_window, target_window),
                            run_time=run_time * 0.3
                        )
                        self.wait(run_time * 0.7)
            
            # Fade out everything AFTER the voiceover completes
            self.play(FadeOut(code_window), run_time=total_duration * 0.1)
        else:
            # Fallback block for manual testing
            self.play(FadeIn(code_window), run_time=1.0)
            
            for hl in highlights:
                hl_start = 0
                hl_end = 0
                if "search_string" in hl:
                    search_str = hl["search_string"]
                    for i, line in enumerate(target_lines):
                        if search_str in line:
                            hl_start = i
                            hl_end = i + hl.get("lines_count", 1) - 1
                            break
                else:
                    hl_start = hl["lines"][0] - code_range[0]
                    hl_end = hl["lines"][-1] - code_range[0]
                    
                if hl_start >= 0 and hl_end < len(code_window.code_lines):
                    active_group = VGroup(*[code_window.code_lines[i] for i in range(hl_start, min(hl_end + 1, len(code_window.code_lines)))])
                    shift_y = -active_group.get_center()[1]
                    shift_vector = np.array([0, shift_y, 0])
                    
                    target_window = code_window.copy()
                    target_window.shift(shift_vector)
                    
                    for i, line in enumerate(target_window.code_lines):
                        target_opacity = 1.0 if (hl_start <= i <= hl_end) else 0.2
                        line.set_opacity(target_opacity)
                    for i, num in enumerate(target_window.line_numbers):
                        target_opacity = 1.0 if (hl_start <= i <= hl_end) else 0.2
                        num.set_opacity(target_opacity)
                        
                    self.play(
                        Transform(code_window, target_window),
                        run_time=0.5
                    )
                    self.wait(2.0)
            
            self.play(FadeOut(code_window), run_time=1.0)
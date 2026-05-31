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
        
        # Coordinate system
        axes = ThreeDAxes(
            x_range=[0, 5, 1], 
            y_range=[0, 5, 1], 
            z_range=[0, 5, 1],
            x_length=5, y_length=5, z_length=5
        ).move_to(ORIGIN)
        
        # Label axes according to rule
        axes.x_axis.add_numbers(font_size=24)
        axes.y_axis.add_numbers(font_size=24)
        axes.z_axis.add_numbers(font_size=24)
        
        x_label = axes.get_x_axis_label("X")
        y_label = axes.get_y_axis_label("Y")
        z_label = axes.get_z_axis_label("Z")
        
        # Create a 2D grid on the XY plane
        grid_2d = VGroup()
        for x in range(1, 6):
            grid_2d.add(Line(axes.c2p(x, 0, 0), axes.c2p(x, 5, 0), color=BLUE_D, stroke_width=2, stroke_opacity=0.5))
        for y in range(1, 6):
            grid_2d.add(Line(axes.c2p(0, y, 0), axes.c2p(5, y, 0), color=BLUE_D, stroke_width=2, stroke_opacity=0.5))
            
        # Create a 3D mesh
        mesh_3d = VGroup()
        for x in range(0, 6):
            for y in range(0, 6):
                mesh_3d.add(Line(axes.c2p(x, y, 0), axes.c2p(x, y, 5), color=BLUE_E, stroke_width=1, stroke_opacity=0.6))
        for x in range(0, 6):
            for z in range(1, 6):
                mesh_3d.add(Line(axes.c2p(x, 0, z), axes.c2p(x, 5, z), color=BLUE_E, stroke_width=1, stroke_opacity=0.6))
        for y in range(0, 6):
            for z in range(1, 6):
                mesh_3d.add(Line(axes.c2p(0, y, z), axes.c2p(5, y, z), color=BLUE_E, stroke_width=1, stroke_opacity=0.6))
        
        # UI Elements
        superscripts = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "d": "ᵈ"}
        counter = Text("10ᵈ", font_size=72, color=RED).to_edge(UP)
        curse_text = Text("The Curse of Dimensionality", font_size=36, color=WHITE).next_to(counter, DOWN)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Step 1: 1D Axis
            self.play(Create(axes.x_axis), Write(x_label), run_time=d * 0.05)
            
            # Step 2: 2D Axis
            self.play(Create(axes.y_axis), Write(y_label), run_time=d * 0.05)
            
            # Step 3: 2D Grid
            self.play(Create(grid_2d), run_time=d * 0.1)
            
            # Step 4: 3D Axis
            self.play(Create(axes.z_axis), Write(z_label), run_time=d * 0.05)
            
            # Step 5: 3D Mesh
            self.play(Create(mesh_3d), run_time=d * 0.15)
            
            # The Explosion of dimensions
            self.add_fixed_in_frame_mobjects(counter, curse_text)
            self.play(FadeIn(counter), run_time=d * 0.1)
            
            # Animate the counter 10^3 -> 10^50
            for val in [10, 20, 50]:
                exp_str = "".join(superscripts.get(c, c) for c in str(val))
                new_counter = Text(f"10{exp_str} Grid Nodes", font_size=54, color=RED).to_edge(UP)
                self.add_fixed_in_frame_mobjects(new_counter)
                new_counter.set_opacity(0)
                self.play(
                    FadeOut(counter),
                    new_counter.animate.set_opacity(1),
                    run_time=d * 0.1
                )
                counter = new_counter
            
            self.play(
                FadeIn(curse_text), 
                mesh_3d.animate.set_color(RED).set_stroke(width=2, opacity=0.8),
                grid_2d.animate.set_color(RED).set_stroke(width=2, opacity=0.8),
                run_time=d * 0.1
            )
            
            # Shatter and clear
            self.move_camera(
                phi=0 * DEGREES, theta=-90 * DEGREES, # Back to 2D
                run_time=d * 0.1,
                added_anims=[
                    FadeOut(mesh_3d), FadeOut(grid_2d), FadeOut(axes), 
                    FadeOut(counter), FadeOut(curse_text), 
                    FadeOut(x_label), FadeOut(y_label), FadeOut(z_label)
                ]
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
        # 1. INITIAL CAMERA SETUP
        # Start in a 2D perspective looking straight down the Z-axis. 
        # This allows a seamless transition from the 1D Monte Carlo scene.
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=0.8)
        
        # 2. SETUP 3D AXES
        # X = Time (0 to 1 year), Y = Stock 1, Z = Stock 2
        # We shift it slightly down to ensure labels don't get clipped by the camera view.
        axes = ThreeDAxes(
            x_range=[0, 1, 0.2], y_range=[60, 140, 20], z_range=[60, 140, 20],
            x_length=7, y_length=5, z_length=5
        ).shift(DOWN * 1.5)
        
        # Add numerical ticks for mathematical clarity
        axes.add_coordinates()
        
        x_label = axes.get_x_axis_label(Tex("Time ($t$)"))
        y_label = axes.get_y_axis_label(Tex("Stock 1 ($S_1$)"))
        z_label = axes.get_z_axis_label(Tex("Stock 2 ($S_2$)"))

        # 3. DEFINE THE MATHEMATICAL BOUNDARY (THE HYPERBOLA)
        # The payoff for a geometric basket option is max(sqrt(S1 * S2) - K, 0).
        # Assuming Strike (K) = 100, the option is In-The-Money (ITM) when S1 * S2 > 10000.
        # Solving for S2, we get S2 > 10000 / S1. This plots a hyperbolic curve.
        
        # Draw the exact yellow boundary curve on the terminal plane (t = 1.0)
        boundary_curve = ParametricFunction(
            lambda v: axes.c2p(1.0, v, 10000/v),
            t_range=[71.4, 140], # The bounds are calculated as 10000 / 140 = 71.4
            color=YELLOW, stroke_width=4
        )
        
        # 4. CONSTRUCT THE IN-THE-MONEY (ITM) SURFACE
        # To shade the area *above* the curve, we manually trace the polygon.
        itm_points = []
        
        # Step A: Trace the hyperbolic curve from left to right
        for y_val in np.linspace(71.4, 140, 50):
            itm_points.append(axes.c2p(1.0, y_val, 10000/y_val))
            
        # Step B: Close the polygon by pinning it to the top-right and top-left bounds of our axes
        itm_points.append(axes.c2p(1.0, 140, 140))
        itm_points.append(axes.c2p(1.0, 71.4, 140))
        
        # Step C: Render it as a flat polygon. `set_points_as_corners` ensures the 
        # corners remain sharp and don't get smoothed by Bezier interpolation.
        itm_surface = VMobject(fill_opacity=0.3, stroke_width=0).set_color(GREEN)
        itm_surface.set_points_as_corners(itm_points)

        # The mathematical equation to display at the end of the scene
        eq = MathTex(r"V_0 = e^{-rT} \mathbb{E}[\max(\sqrt{S_1 S_2} - K, 0)]", font_size=36).to_corner(UR)

        # 5. VOICOVER & ANIMATION SEQUENCE
        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Animate the 2D view first
            self.play(Create(axes.x_axis), Create(axes.y_axis), Write(x_label), Write(y_label), run_time=d * 0.1)
            
            # Rotate the camera to 3D, dynamically revealing the Z-axis (Stock 2)
            self.move_camera(
                phi=75 * DEGREES, theta=-45 * DEGREES, 
                run_time=d * 0.2, 
                added_anims=[Create(axes.z_axis), Write(z_label)]
            )
            
            # 6. SIMULATE GEOMETRIC BROWNIAN MOTION (GBM)
            np.random.seed(42)
            path_curves = []
            
            dt = 1.0 / 50 # 50 time steps for a detailed, high-resolution path
            r = 0.05
            vol = 0.2
            
            # Pre-compute constants for speed
            drift = (r - 0.5 * vol**2) * dt
            vol_sqrt_dt = vol * np.sqrt(dt)
            
            for _ in range(4):
                S1 = [100.0]
                S2 = [100.0]
                for _ in range(50):
                    # Multiplicative shock creates true Geometric Brownian Motion
                    S1.append(S1[-1] * np.exp(drift + vol_sqrt_dt * np.random.randn()))
                    S2.append(S2[-1] * np.exp(drift + vol_sqrt_dt * np.random.randn()))
                
                t_vals = np.linspace(0, 1, 51)
                pts = [axes.c2p(t, y, z) for t, y, z in zip(t_vals, S1, S2)]
                
                # CRITICAL: `set_points_as_corners` connects the points with straight, rigid lines.
                # This guarantees the jagged, discontinuous visual style of stochastic calculus, 
                # rather than the artificially smooth Bezier curves.
                curve = VMobject().set_points_as_corners(pts).set_color(BLUE)
                path_curves.append(curve)

            # Draw the 3D paths shooting through space
            self.play(*[Create(p) for p in path_curves], run_time=d * 0.3)
            
            # Reveal the terminal boundary and illuminate the ITM region
            self.play(Create(boundary_curve), run_time=d * 0.1)
            self.play(FadeIn(itm_surface), run_time=d * 0.1)
            
            # Pin the pricing equation to the camera frame (so it doesn't rotate in 3D space)
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
            up_p["line_graph"].set_fill(opacity=0)
            up_paths.append(up_p)
            
            # Down-shocked path (starts at 95)
            S_dn = [95]
            for i in range(50):
                S_dn.append(S_dn[-1] * np.exp((0.05 - 0.5*0.04)*dt + 0.2*np.sqrt(dt)*shocks[i]))
            dn_p = axes.plot_line_graph(x_values=np.linspace(0, 1, 51), y_values=S_dn, line_color=RED, add_vertex_dots=False)
            dn_p["line_graph"].set_fill(opacity=0)
            dn_paths.append(dn_p)

        box_1d = VGroup(Rectangle(width=3, height=0.6, color=BLUE, fill_opacity=0.2), Text("1 Asset = 2 Sims", font_size=20)).next_to(axes, DOWN)
        plot_group = VGroup(
            axes, x_label, y_label,
            *[bp["line_graph"] for bp in base_paths],
            *[up["line_graph"] for up in up_paths],
            *[dn["line_graph"] for dn in dn_paths]
        )

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Write(eq), run_time=d * 0.05)
            self.play(Create(axes), Write(x_label), Write(y_label), run_time=1.5)
            self.play(*[Create(bp) for bp in base_paths], run_time=d * 0.3)
            
            # Bumps
            self.play(*[Create(up) for up in up_paths], run_time=d * 0.3)
            self.play(*[Create(dn) for dn in dn_paths], run_time=d * 0.3)
            self.play(FadeIn(box_1d), run_time=d * 0.1)
            
            # Scale to 50 assets (Grid of Miniaturized Axes)
            grid = VGroup(*[plot_group.copy().scale(0.12) for _ in range(36)])
            grid.arrange_in_grid(rows=6, cols=6, buff=0.2).move_to(ORIGIN)
            
            self.play(
                Transform(plot_group, grid),
                FadeOut(box_1d),
                run_time=d * 0.2
            )
            
            final_text = Text("Total Paths: 1,000,000+", color=RED, font_size=40).move_to(ORIGIN)
            self.play(FadeIn(final_text, scale=1.5), plot_group.animate.set_opacity(0.1), run_time=d * 0.1)
            
            # Fade everything out
            self.play(FadeOut(plot_group), FadeOut(final_text), FadeOut(eq), run_time=d * 0.1)


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
        nn_icon = VGroup(Circle(radius=0.4, color=BLUE, fill_opacity=0.2), Text("NN", font_size=20)).move_to(RIGHT*2 + DOWN*1.5)
        y0_label = Text("Initial Cash (Y₀)", font_size=24, color=YELLOW).next_to(nn_icon, UP)
        
        # Equations
        bsde_eq = MathTex(r"dY_t = rY_t dt + Z_t dW_t", font_size=36).to_corner(DR).shift(UP * 1.5)
        z_def = Tex(r"$Z = \sigma \Delta S$", font_size=28, color=GREEN).next_to(bsde_eq, UP)

        # Simulation Parameters
        np.random.seed(42)
        dt = 0.02
        S = [100.0]
        for i in range(50):
            S.append(S[-1] * np.exp((0.05 - 0.5*0.04)*dt + 0.2*np.sqrt(dt)*np.random.randn()))
        t_vals = np.linspace(0, 1, 51)
        
        # Simulate corresponding wealth path Y
        np.random.seed(123)
        Y = [10.0]
        for i in range(50):
            dS = S[i+1] - S[i]
            dy = 0.05 * Y[-1] * dt + 0.15 * dS + np.random.randn() * 0.1
            Y.append(Y[-1] + dy)
        Y = np.array(Y)
        Y = 10.0 + (Y - Y[0]) * (11.50 - 10.0) / (Y[-1] - Y[0])
        
        def get_current_S(t):
            idx = min(int(t * 50), 49)
            t_low = t_vals[idx]
            t_high = t_vals[idx+1]
            s_low = S[idx]
            s_high = S[idx+1]
            return s_low + (s_high - s_low) * (t - t_low) / (t_high - t_low)
            
        def get_current_Y(t):
            idx = min(int(t * 50), 49)
            t_low = t_vals[idx]
            t_high = t_vals[idx+1]
            y_low = Y[idx]
            y_high = Y[idx+1]
            return y_low + (y_high - y_low) * (t - t_low) / (t_high - t_low)

        # Dynamic Trackers
        t_tracker = ValueTracker(0.0)
        
        # Live Bar and Counter
        bar_color = [GREEN]
        bar = always_redraw(lambda: Rectangle(
            width=0.8, height=max(0.1, ax_bot.c2p(0, get_current_Y(t_tracker.get_value()))[1] - ax_bot.c2p(0, 0)[1]),
            color=bar_color[0], fill_opacity=0.7
        ).move_to(ax_bot.c2p(0.5, get_current_Y(t_tracker.get_value())/2)))
        
        counter = always_redraw(lambda: Text(f"${get_current_Y(t_tracker.get_value()):.2f}", font_size=24, color=bar_color[0])
                                .next_to(bar, UP, buff=0.1))

        # Evolving stock path
        pts = [ax_top.c2p(t, y) for t, y in zip(t_vals, S)]
        path = VMobject().set_points_as_corners(pts).set_color(BLUE)
        
        # Real-time stock price indicator
        dot = always_redraw(lambda: Dot(
            ax_top.c2p(t_tracker.get_value(), get_current_S(t_tracker.get_value())),
            color=YELLOW, radius=0.08
        ))
        price_label = always_redraw(lambda: Text(
            f"Sₜ = ${get_current_S(t_tracker.get_value()):.2f}",
            font_size=18, color=YELLOW
        ).next_to(dot, UP, buff=0.15))

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Setup split screen
            self.play(Create(ax_top), Write(lbl_top_x), Write(lbl_top_y), Create(ax_bot), Write(lbl_bot), run_time= 0.15)
            
            # Init Y_0
            self.play(FadeIn(nn_icon), Write(y0_label), run_time= 0.1)
            self.play(FadeIn(bar), FadeIn(counter), run_time= 0.1)
            
            # Equation Reveal
            self.play(Write(bsde_eq), Write(z_def), run_time=d * 0.15)
            
            # Gameplay (Draw stock path, randomly update wealth)
            self.add(dot, price_label)
            self.play(
                Create(path),
                t_tracker.animate.set_value(1.0),
                run_time=d * 0.35,
                rate_func=linear
            )
            
            # The Miss
            target_val = 15.0
            target_line = DashedVMobject(ax_bot.plot(lambda x: target_val, color=WHITE))
            target_txt = Text("True Payoff: $15.00", font_size=20).next_to(target_line, RIGHT)
            
            self.play(Create(target_line), FadeIn(target_txt), run_time=d * 0.05)
            
            # Red Bracket
            bracket = BraceBetweenPoints(ax_bot.c2p(1, 11.5), ax_bot.c2p(1, 15), color=RED, direction=RIGHT)
            loss_txt = bracket.get_text("Loss").set_color(RED)
            
            bar_color[0] = RED
            self.play(Create(bracket), FadeIn(loss_txt), run_time=d * 0.05)


# ==============================================================================
# SCENE 5: The Architecture (Backprop & The Evolving Equation)
# ==============================================================================
class Architecture(SciMLScene):
    def construct(self):
        # 1. THE TIMELINE & NODES
        timeline = Line(LEFT*5, RIGHT*3, color=WHITE).shift(DOWN * 1.5)
        # Using 5 nodes (t_0, t_1, t_2, t_3, T)
        nodes = VGroup(*[Circle(radius=0.3, color=BLUE, fill_opacity=0.2).move_to(timeline.point_from_proportion(p)) for p in np.linspace(0, 1, 5)])
        labels = VGroup(*[MathTex(f"t_{i}" if i<4 else "T", font_size=24).next_to(nodes[i], DOWN) for i in range(5)])
        
        # 2. THE MASTER EQUATION (Discretized BSDE)
        # Y_{t+1} = Y_t + rY_t dt + Z_t dW_t
        eq = MathTex(
            r"Y_{t+1}", r"=", r"Y_t", r"+ r Y_t \Delta t", r"+", r"Z_t", r"\Delta W_t"
        ).scale(1.2).to_edge(UP).shift(DOWN * 0.5)
        
        # Color coding: Wealth is Green, NN Hedge is Yellow, Noise is Blue
        eq[0].set_color(GREEN)   # Y_{t+1}
        eq[2].set_color(GREEN)   # Y_t
        eq[3][2:4].set_color(GREEN) # Y_t inside the drift term
        eq[5].set_color(YELLOW)  # Z_t
        eq[6].set_color(BLUE_C)  # \Delta W_t

        # Explanatory Braces for the Equation
        brace_Z = Brace(eq[5], DOWN, buff=0.1)
        text_Z = Tex("NN Hedge", font_size=32).set_color(YELLOW)
        brace_Z.put_at_tip(text_Z)
        
        brace_dW = Brace(eq[4:], DOWN, buff=0.1)
        # Shift Trading PnL down so it doesn't overlap with the NN Hedge brace/label
        brace_dW.shift(DOWN * 0.95)
        text_dW = Tex("Trading PnL", font_size=32)
        brace_dW.put_at_tip(text_dW)

        eq_group = VGroup(eq, brace_Z, text_Z, brace_dW, text_dW)

        # 3. PAYOFF WALL & DIALS
        payoff_wall = Rectangle(width=0.2, height=2, color=WHITE, fill_opacity=1).next_to(nodes[-1], RIGHT, buff=1)
        wall_txt = Text("True Payoff", font_size=20).next_to(payoff_wall, UP)
        
        # Create mechanical dials with rotating needles
        def create_dial(label_mob, color):
            circle = Circle(radius=0.4, color=color, stroke_width=3)
            needle = Line(circle.get_center(), circle.get_top(), color=WHITE).scale(0.8)
            label_mob.next_to(circle, UP, buff=0.15)
            return VGroup(circle, needle, label_mob), needle

        dial_w, needle_w = create_dial(Text("NN Weights", font_size=24), YELLOW)
        dial_y0, needle_y0 = create_dial(MathTex(r"Y_0\text{ Dial}", font_size=24), GREEN)
        
        # Place dials at the center of the screen (safely above the timeline)
        dials = VGroup(dial_w, dial_y0).arrange(RIGHT, buff=2.0).move_to(UP * 0.1).move_to(LEFT*1.5)

        # 4. ANIMATION SEQUENCE
        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Setup Timeline and Master Equation
            self.play(Create(timeline), FadeIn(nodes), FadeIn(labels), run_time=d * 0.1)
            self.play(Write(eq), run_time=d * 0.1)
            self.play(FadeIn(brace_Z), FadeIn(text_Z), FadeIn(brace_dW), FadeIn(text_dW), run_time=d * 0.1)
            
            # The Forward Pass
            pulse = Dot(color=GREEN).move_to(nodes[0].get_center())
            self.play(FadeIn(pulse), FadeIn(dials), run_time=d * 0.05)
            
            for i in range(4):
                # 1. Node flashes yellow as the NN outputs Z_t
                z_label = MathTex(f"Z_{{{i}}}", font_size=24, color=YELLOW).next_to(nodes[i], UP)
                self.play(
                    nodes[i].animate.set_color(YELLOW),
                    FadeIn(z_label, shift=UP),
                    eq[5].animate.scale(1.2).set_color(WHITE), # Highlight Z_t in eq
                    run_time=d * 0.01
                )
                
                # 2. Pulse (Wealth) moves forward to next step
                self.play(
                    eq[5].animate.scale(1/1.2).set_color(YELLOW),
                    nodes[i].animate.set_color(BLUE),
                    pulse.animate.move_to(nodes[i+1].get_center()), 
                    FadeOut(z_label),
                    eq[0].animate.scale(1.2).set_color(WHITE), # Highlight Y_{t+1} in eq
                    run_time=d * 0.01
                )
                self.play(eq[0].animate.scale(1/1.2).set_color(GREEN), run_time=d * 0.01)
                
            # Collision and Loss
            self.play(FadeIn(payoff_wall), FadeIn(wall_txt), pulse.animate.move_to(payoff_wall.get_left()), run_time=d * 0.01)
            
            # Loss Bracket
            loss_bracket = BraceBetweenPoints(pulse.get_center(), payoff_wall.get_right(), color=RED, direction=UP)
            loss_text = loss_bracket.get_text("Loss (MSE)").set_color(RED)
            
            self.play(
                FadeIn(loss_bracket), FadeIn(loss_text), 
                pulse.animate.set_color(RED).scale(1.5), 
                run_time=d * 0.1
            )
            
            # The Backward Pass
            self.play(FadeOut(loss_bracket), FadeOut(loss_text), run_time=d * 0.05)
            for i in range(4, -1, -1):
                self.play(pulse.animate.move_to(nodes[i].get_center()), run_time=d * 0.04)
                
            # Update Dials (Turn the needles)
            self.play(
                Rotate(needle_w, angle=PI/1.5, about_point=dial_w[0].get_center()), 
                Rotate(needle_y0, angle=-PI/2, about_point=dial_y0[0].get_center()), 
                pulse.animate.set_opacity(0),
                run_time=d * 0.08
            )

# ==============================================================================
# SCENE 6: Code Walkthrough
# ==============================================================================
class CodeWalkthroughScene(SciMLScene):
    def construct(self):
        scene_id = self.scene_config.get("id", "")
        
        # Read the config values or use fallbacks
        code_file = self.scene_config.get("code_file", "code/deep_bsde_solver.py")
        default_highlights = [
            {"lines": [25, 36]},
            {"lines": [38, 54]},
            {"lines": [56, 72]},
            {"lines": [77, 102]}
        ]
        highlights = self.scene_config.get("highlights", default_highlights)
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
            lines = [f"# Line {i}\n" for i in range(1, 200)]
            
        def render_snippet(hl):
            if "search_string" in hl:
                search_str = hl["search_string"]
                hl_start = 0
                hl_end = 0
                for i, line in enumerate(lines):
                    if search_str in line:
                        hl_start = i
                        hl_end = i + hl.get("lines_count", 1) - 1
                        break
            else:
                hl_start = hl["lines"][0] - 1
                hl_end = hl["lines"][-1] - 1
                
            snippet_lines = lines[hl_start:hl_end + 1]
            
            # Sanitize
            cleaned_lines = []
            for line in snippet_lines:
                if line.strip() == "":
                    cleaned_lines.append(" \n")
                else:
                    cleaned_lines.append(line.replace("\t", "    "))
                    
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.writelines(cleaned_lines)
                
            snippet_code = Code(
                code_file=str(temp_file_path),
                line_numbers_from=hl_start + 1,
                tab_width=4,
                background="window",
                language="python",
                formatter_style="monokai",
                paragraph_config={"disable_ligatures": False}
            )
            return snippet_code.scale(0.65).move_to(ORIGIN)
            
        if "scene_6" in scene_id:
            with self.voiceover(text=voiceover_text, path=self.voiceover_path) as tracker:
                total_duration = tracker.duration
                num_hl = max(len(highlights), 1)
                segment_durations = [1.0 / num_hl] * num_hl
                
                for idx, hl in enumerate(highlights):
                    snippet_code = render_snippet(hl)
                    run_time = total_duration * segment_durations[idx]
                    
                    fade_time = min(0.5, run_time * 0.1)
                    wait_time = run_time - (2 * fade_time)
                    if wait_time < 0:
                        wait_time = 0
                        fade_time = run_time / 2
                    
                    self.play(FadeIn(snippet_code), run_time=fade_time)
                    self.wait(wait_time)
                    self.play(FadeOut(snippet_code), run_time=fade_time)
        else:
            # Fallback block for manual testing
            for hl in highlights:
                snippet_code = render_snippet(hl)
                self.play(FadeIn(snippet_code), run_time=0.5)
                self.wait(1.5)
                self.play(FadeOut(snippet_code), run_time=0.5)
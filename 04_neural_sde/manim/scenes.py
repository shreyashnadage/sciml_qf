from manim import *
import numpy as np
import sys
import os
import json
from pathlib import Path
from manim_voiceover import VoiceoverScene
from manim_ml.neural_network import NeuralNetwork, FeedForwardLayer

# Add the project root to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from qwen_voiceover import QwenSpeechService

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


# ---------------------------------------------------------
# ACT 1: Continuous vs Jump Paths
# ---------------------------------------------------------
class Act1_RoughPaths(SciMLScene):
    def construct(self):
        # Setup Two Axes
        axes_gbm = Axes(x_range=[0, 100, 20], y_range=[0.8, 1.5, 0.2], x_length=8, y_length=2.5).shift(UP * 1.5)
        axes_jump = Axes(x_range=[0, 100, 20], y_range=[0.5, 2.0, 0.5], x_length=8, y_length=2.5).shift(DOWN * 2)

        # Labels
        label_gbm = Text("Textbook Market (Continuous GBM)", font_size=24, color=BLUE).next_to(axes_gbm, UP)
        label_jump = Text("Real Market (Jumps & Microstructure Noise)", font_size=24, color=RED).next_to(axes_jump, UP)

        # Generate Data
        np.random.seed(42)
        n_steps = 200
        dt = 1.0 / n_steps
        
        # Smooth GBM
        dW = np.random.normal(0, np.sqrt(dt), n_steps)
        gbm_path = np.exp(np.cumsum(0.05 * dt + 0.2 * dW))
        gbm_path = np.insert(gbm_path, 0, 1.0)
        
        # High Frequency Jump Diffusion
        jumps = np.random.poisson(0.1, n_steps) * np.random.normal(0, 0.15, n_steps)
        noise = np.random.normal(0, 0.02, n_steps) # Microstructure
        jump_path = np.exp(np.cumsum(0.05 * dt + 0.3 * dW + jumps) + noise)
        jump_path = np.insert(jump_path, 0, 1.0)

        # Plot Graphs
        x_vals = np.linspace(0, 100, n_steps + 1)
        graph_gbm = axes_gbm.plot_line_graph(x_values=x_vals, y_values=gbm_path, line_color=BLUE, add_vertex_dots=False, stroke_width=4)
        graph_jump = axes_jump.plot_line_graph(x_values=x_vals, y_values=jump_path, line_color=RED, add_vertex_dots=False, stroke_width=2)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Create(axes_gbm), Write(label_gbm), run_time=d * 0.1)
            self.play(Create(graph_gbm), run_time=d * 0.2)
            
            self.play(Create(axes_jump), Write(label_jump), run_time=d * 0.1)
            self.play(Create(graph_jump), run_time=d * 0.4)
            self.wait(d * 0.2)

# ---------------------------------------------------------
# ACT 2: The Path Signature (Scanner to Box)
# ---------------------------------------------------------
class Act2_PathSignature(SciMLScene):
    def construct(self):
        axes = Axes(x_range=[0, 100], y_range=[0.5, 2.0], x_length=10, y_length=4).shift(DOWN * 1)
        
        # Jagged Path
        np.random.seed(42)
        n_steps = 100
        y_vals = np.exp(np.cumsum(np.random.normal(0, 0.05, n_steps)))
        y_vals = np.insert(y_vals, 0, 1.0)
        x_vals = np.linspace(0, 100, n_steps + 1)
        path = axes.plot_line_graph(x_values=x_vals, y_values=y_vals, line_color=RED, add_vertex_dots=False)
        
        self.add(axes, path)

        # Scanner Line
        scanner = Line(axes.c2p(0, 2.5), axes.c2p(0, 0), color=YELLOW, stroke_width=4)
        scan_glow = scanner.copy().set_stroke(width=15, opacity=0.3, color=YELLOW)
        scan_group = VGroup(scanner, scan_glow)

        # Attribute Boxes
        def create_box(text, color):
            rect = RoundedRectangle(corner_radius=0.1, height=0.8, width=3, color=color, fill_opacity=0.2)
            label = Text(text, font_size=24).move_to(rect.get_center())
            return VGroup(rect, label)

        box_shape = create_box("Shape & Direction", BLUE).to_edge(UP).shift(LEFT * 4)
        box_area = create_box("Swept Area", GREEN).to_edge(UP)
        box_lag = create_box("Lead-Lag Relations", PURPLE).to_edge(UP).shift(RIGHT * 4)

        # Final Signature Box
        final_box = RoundedRectangle(corner_radius=0.2, height=1.5, width=6, color=GOLD, fill_opacity=0.3)
        final_text = Text("Path Signature", font_size=36, weight=BOLD).move_to(final_box)
        final_sig = VGroup(final_box, final_text).to_edge(UP)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Start Scan
            self.play(FadeIn(scan_group), run_time=d * 0.05)
            self.play(scan_group.animate.move_to(axes.c2p(100, 1.25)), run_time=d * 0.35, rate_func=linear)
            
            # Extract Attributes
            self.play(FadeIn(box_shape, shift=DOWN), run_time=d * 0.1)
            self.play(FadeIn(box_area, shift=DOWN), run_time=d * 0.1)
            self.play(FadeIn(box_lag, shift=DOWN), run_time=d * 0.1)
            self.play(FadeOut(scan_group), run_time=d * 0.05)
            
            # Combine into Signature
            self.play(
                ReplacementTransform(VGroup(box_shape, box_area, box_lag), final_sig),
                run_time=d * 0.2
            )
            self.play(Indicate(final_sig, color=WHITE, scale_factor=1.1), run_time=d * 0.05)


# ---------------------------------------------------------
# ACT 3: The Neural SDE (Algebra Transformation)
# ---------------------------------------------------------
class Act3_NeuralSDE(SciMLScene):
    def construct(self):
        # Classic Equation
        eq_classic = MathTex(
            r"dS", r"=", r"\mu(t, S)", r"dt", r"+", r"\sigma(t, S)", r"dW",
            font_size=60
        )
        
        # Neural Network Diagrams using manim-ml
        nn_mu = Group(
            NeuralNetwork([
                FeedForwardLayer(num_nodes=1, node_color=GREEN),
                FeedForwardLayer(num_nodes=5, node_color=GREEN),
                FeedForwardLayer(num_nodes=5, node_color=GREEN),
                FeedForwardLayer(num_nodes=1, node_color=GREEN)
            ], layer_spacing=0.2)
        ).scale(0.22).move_to(eq_classic[2].get_center())

        nn_sigma = Group(
            NeuralNetwork([
                FeedForwardLayer(num_nodes=1, node_color=ORANGE),
                FeedForwardLayer(num_nodes=5, node_color=ORANGE),
                FeedForwardLayer(num_nodes=5, node_color=ORANGE),
                FeedForwardLayer(num_nodes=1, node_color=ORANGE)
            ], layer_spacing=0.2)
        ).scale(0.22).move_to(eq_classic[5].get_center())

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Write(eq_classic), run_time=d * 0.2)
            self.wait(d * 0.1)
            
            # Highlight terms to replace
            self.play(Indicate(eq_classic[2], color=GREEN), Indicate(eq_classic[5], color=ORANGE), run_time=d * 0.1)
            
            # Physically swap the algebraic terms for NN diagrams
            self.play(
                FadeTransform(eq_classic[2], nn_mu),
                FadeTransform(eq_classic[5], nn_sigma),
                run_time=d * 0.4
            )
            self.wait(d * 0.2)

# ---------------------------------------------------------
# ACT 4: Generative Signature Loss (Split Screen)
# ---------------------------------------------------------
class Act4_GenerativeLoss(SciMLScene):
    def construct(self):
        # Left Side (Reality)
        real_title = Text("Real Market", font_size=24, color=BLUE).to_corner(UL).shift(RIGHT)
        axes_real = Axes(x_range=[0, 10], y_range=[0, 2], x_length=4, y_length=2).next_to(real_title, DOWN)
        path_real = axes_real.plot(lambda x: 1 + 0.1*x + 0.2*np.sin(5*x), color=BLUE)
        
        arrow_real = Arrow(UP, DOWN, color=WHITE).next_to(axes_real, DOWN)
        box_real = RoundedRectangle(height=0.8, width=2.5, color=BLUE, fill_opacity=0.3).next_to(arrow_real, DOWN)
        text_real = MathTex(r"\text{Sig}_{real}", font_size=32).move_to(box_real)

        # Right Side (Generator)
        gen_title = Text("Neural SDE", font_size=24, color=RED).to_corner(UR).shift(LEFT * 1.5)
        axes_gen = Axes(x_range=[0, 10], y_range=[0, 2], x_length=4, y_length=2).next_to(gen_title, DOWN)
        path_gen = axes_gen.plot(lambda x: 1 + 0.05*x + 0.4*np.cos(3*x), color=RED) # Intentionally wrong shape
        
        arrow_gen = Arrow(UP, DOWN, color=WHITE).next_to(axes_gen, DOWN)
        box_gen = RoundedRectangle(height=0.8, width=2.5, color=RED, fill_opacity=0.3).next_to(arrow_gen, DOWN)
        text_gen = MathTex(r"\text{Sig}_{pred}", font_size=32).move_to(box_gen)

        # Center Loss
        loss_eq = MathTex(
            r"\text{Loss} = \text{MSE}\left( ", r"\text{Sig}_{real}", r", ", r"\text{Sig}_{pred}", r" \right)",
            font_size=48
        ).to_edge(DOWN).shift(UP * 0.5)
        loss_eq[1].set_color(BLUE)
        loss_eq[3].set_color(RED)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            
            # Left side
            self.play(Write(real_title), Create(axes_real), Create(path_real), run_time=d * 0.1)
            self.play(GrowArrow(arrow_real), FadeIn(box_real), Write(text_real), run_time=d * 0.1)
            
            # Right side
            self.play(Write(gen_title), Create(axes_gen), Create(path_gen), run_time=d * 0.1)
            self.play(GrowArrow(arrow_gen), FadeIn(box_gen), Write(text_gen), run_time=d * 0.1)
            
            # Draw Loss Connection
            self.play(Write(loss_eq), run_time=d * 0.2)
            
            # Animate Convergence (The Right side adjusts to match Left)
            path_gen_fixed = axes_gen.plot(lambda x: 1 + 0.1*x + 0.2*np.sin(5*x), color=ORANGE)
            self.play(
                Transform(path_gen, path_gen_fixed),
                box_gen.animate.set_color(ORANGE),
                loss_eq.animate.scale(1.1).set_color(YELLOW),
                run_time=d * 0.3
            )
            self.wait(d * 0.1)

# ---------------------------------------------------------
# ACT 5: Code Walkthrough
# ---------------------------------------------------------
class CodeWalkthroughScene(SciMLScene):
    def construct(self):
        scene_id = self.scene_config.get("id", "")
        
        # Read the config values or use fallbacks
        code_file = self.scene_config.get("code_file", "code/neural_sde_model.py")
        
        # Resolve to the correct file path and default highlights
        if "neural_sde_model.py" in code_file or "04_neural_sde.py" in code_file:
            code_file = "code/04_neural_sde.py"
            default_highlights = [
                {"lines": [34, 36]}, # Signatory path signature
                {"lines": [41, 71]}, # LatentNeuralSDE definition
                {"lines": [86, 95]}  # Training loop & Signature loss
            ]
        else:
            default_highlights = [
                {"lines": [34, 36]},
                {"lines": [41, 71]},
                {"lines": [86, 95]}
            ]
            
        highlights = self.scene_config.get("highlights", default_highlights)
        # If highlights are the outdated ones from old neural_sde_model.py, override them
        if len(highlights) == 3 and highlights[0].get("lines") == [22, 24]:
            highlights = [
                {"lines": [34, 36]},
                {"lines": [41, 71]},
                {"lines": [86, 95]}
            ]
            
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
            
            # Sanitize to fix the Manim empty-line Pygments crash bug
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
            
        if "scene_5" in scene_id:
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
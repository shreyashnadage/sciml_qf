from manim import *
import numpy as np
from scipy.stats import norm
import sys
import os
import json
from pathlib import Path
from manim_voiceover import VoiceoverScene
import torch

# Add the project root to sys.path so we can import qwen_voiceover
root_dir = Path(__file__).resolve().parents[2] # Adjust if needed
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from qwen_voiceover import QwenSpeechService

# ==========================================
# BASE CLASSES & HELPER FUNCTIONS
# ==========================================

class SciMLScene(VoiceoverScene):
    def setup(self):
        config_path = os.environ.get("SCENE_CONFIG_PATH")
        if not config_path or not os.path.exists(config_path):
            self.scene_config = {
                "id": "manual", "voiceover": "This is fallback voiceover text.",
                "module_dir": str(Path(__file__).resolve().parents[2]),
                "global_config": {"voice": {"speaker": "Ryan"}}
            }
        else:
            with open(config_path, "r") as f: self.scene_config = json.load(f)
        media_dir = os.path.join(self.scene_config.get("module_dir", "."), "media", "voiceovers")
        speaker = self.scene_config.get("global_config", {}).get("voice", {}).get("speaker", "Ryan")
        self.set_speech_service(QwenSpeechService(speaker=speaker, cache_dir=media_dir))
    
    @property
    def voiceover_path(self):
        return os.path.basename(self.scene_config["audio_path"]) if "audio_path" in self.scene_config else None

class SciMLThreeDScene(ThreeDScene, VoiceoverScene):
    def setup(self):
        config_path = os.environ.get("SCENE_CONFIG_PATH")
        if not config_path or not os.path.exists(config_path):
            self.scene_config = {
                "id": "manual", "voiceover": "This is fallback voiceover text.",
                "module_dir": str(Path(__file__).resolve().parents[2]),
                "global_config": {"voice": {"speaker": "Ryan"}}
            }
        else:
            with open(config_path, "r") as f: self.scene_config = json.load(f)
        media_dir = os.path.join(self.scene_config.get("module_dir", "."), "media", "voiceovers")
        speaker = self.scene_config.get("global_config", {}).get("voice", {}).get("speaker", "Ryan")
        self.set_speech_service(QwenSpeechService(speaker=speaker, cache_dir=media_dir))
    
    @property
    def voiceover_path(self):
        return os.path.basename(self.scene_config["audio_path"]) if "audio_path" in self.scene_config else None

def bs_call(S, K, T, sigma, r):
    if T <= 1e-4: return np.maximum(S - K, 0.0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def create_tweet_card(name, handle, lines, avatar_img_path):
    bg = RoundedRectangle(corner_radius=0.3, height=4.5, width=10, color=WHITE, stroke_opacity=0.3, fill_color=BLACK, fill_opacity=0.8)
    avatar = ImageMobject(avatar_img_path).scale_to_fit_height(0.8)
    avatar.move_to(bg.get_corner(UL) + RIGHT * 1 + DOWN * 1)
    
    avatar_border = Circle(radius=0.4, color=WHITE, stroke_width=2).move_to(avatar.get_center())
    
    name_text = Text(name, font_size=28, weight=BOLD).next_to(avatar_border, RIGHT, buff=0.3).align_to(avatar_border, UP).shift(DOWN*0.1)
    handle_text = Text(handle, font_size=20, color=GRAY).next_to(name_text, DOWN, buff=0.1).align_to(name_text, LEFT)
    content = VGroup(*[Text(line, font_size=24, color=WHITE) for line in lines])
    content.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    content.next_to(handle_text, DOWN, buff=0.4).align_to(name_text, LEFT)
    return Group(bg, avatar, avatar_border, name_text, handle_text, content)


# ==========================================
# INDIVIDUAL SCENES FOR PIPELINE
# ==========================================

class Beat1_RackauckasCard(SciMLScene):
    def construct(self):
        avatar_path = os.path.join(self.scene_config.get("module_dir", "."), "00_sciml_course_teaser", "media", "images", "christopherrackauckas83_small.webp")
        # Fallback check
        if not os.path.exists(avatar_path):
            avatar_path = os.path.join(self.scene_config.get("module_dir", "."), "media", "images", "christopherrackauckas83_small.webp")
        quote = create_tweet_card(
            name="Chris Rackauckas", 
            handle="@ChrisRackauckas • Lead Developer, SciML",
            lines=[
                "The trend is merging the two disciplines...",
                "Allowing explainable models that are data-driven,",
                "utilizing the knowledge encapsulated in centuries",
                "of scientific literature."
            ],
            avatar_img_path=avatar_path
        )
        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(FadeIn(quote, shift=UP*0.5), run_time=d * 0.2)
            self.wait(d * 0.6)
            self.play(FadeOut(quote, shift=UP*0.5), run_time=d * 0.2)


class Beat2_TangentPanic(MovingCameraScene, VoiceoverScene):
    def setup(self):
        MovingCameraScene.setup(self)
        SciMLScene.setup(self)

    @property
    def voiceover_path(self):
        return os.path.basename(self.scene_config["audio_path"]) if "audio_path" in self.scene_config else None

    def construct(self):
        K = 100
        axes = Axes(
            x_range=[80, 120, 10], 
            y_range=[0, 20, 5], 
            x_length=8, 
            y_length=5,
            axis_config={"include_numbers": True}
        )
        x_label = axes.get_x_axis_label("S", edge=RIGHT, direction=UP)
        y_label = axes.get_y_axis_label("Payoff", edge=UP, direction=LEFT)
        labels = VGroup(x_label, y_label)
        
        payoff = axes.plot(lambda x: max(x - K, 0), color=BLUE, stroke_width=6)
        kink_point = Dot(axes.c2p(K, 0), color=RED, radius=0.1)
        angle_tracker = ValueTracker(0)
        tangent_line = always_redraw(lambda: Line(LEFT * 2, RIGHT * 2, color=WHITE).rotate(angle_tracker.get_value()).move_to(kink_point.get_center()))

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Create(axes), Write(labels), Create(payoff), run_time=d * 0.2)
            self.play(
                self.camera.frame.animate.scale(0.4).move_to(kink_point.get_center() + UP*0.5),
                FadeIn(kink_point), run_time=d * 0.2
            )
            self.add(tangent_line)
            wobble_time = (d * 0.4) / 8
            for _ in range(4): 
                self.play(angle_tracker.animate.set_value(PI/4), run_time=wobble_time, rate_func=there_and_back)
                self.play(angle_tracker.animate.set_value(-PI/8), run_time=wobble_time, rate_func=there_and_back)
            self.wait(d * 0.2)


class Beat3_CodeWalkthrough(SciMLScene):
    def construct(self):
        code_str = """class PINN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )

    def loss_fn(self, S, t, V_true):
        # 1. Forward Pass
        V_pred = self.net(torch.cat([S, t], dim=1))
        
        # 2. Extract PDE Physics
        physics_loss = compute_pde_residual(V_pred, S, t)
        
        # 3. Minimize MSE + Physics Constraint
        return MSE(V_pred, V_true) + physics_loss
"""
        # Sanitize and write to a temporary file as required by Code rules
        temp_file_path = os.path.join(self.scene_config.get("module_dir", "."), "temp_cleaned_code.py")
        cleaned_lines = []
        for line in code_str.splitlines():
            if line.strip() == "":
                cleaned_lines.append(" \n")
            else:
                cleaned_lines.append(line.replace("\t", "    ") + "\n")
        with open(temp_file_path, "w") as f:
            f.writelines(cleaned_lines)

        # Render the code
        rendered_code = Code(
            code_file=temp_file_path,
            language="python",
            background="window"
        ).scale(0.9).move_to(ORIGIN)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(FadeIn(rendered_code), run_time=d * 0.2)
            
            # Highlight the network definition
            net_lines = VGroup(*rendered_code.code_lines[3:8])
            rect1 = SurroundingRectangle(net_lines, color=YELLOW, fill_opacity=0.2)
            self.play(Create(rect1), run_time=d * 0.2)
            self.wait(d * 0.1)
            
            # Move highlight to the physics loss logic
            loss_lines = VGroup(*rendered_code.code_lines[12:15])
            rect2 = SurroundingRectangle(loss_lines, color=ORANGE, fill_opacity=0.2)
            self.play(Transform(rect1, rect2), run_time=d * 0.2)
            
            self.wait(d * 0.2)
            self.play(FadeOut(rendered_code), FadeOut(rect1), run_time=d * 0.1)


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

class Beat4_ElasticSheet(SciMLThreeDScene):
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
        model_path = os.path.join(root_dir, "02_physics_of_no_arbitrage", "code", "pinn_model.pth")
        
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


class Beat5_Outro(SciMLScene):
    def construct(self):
        title = Text("QuantCatalysts", font_size=64, weight=BOLD)
        title.set_color_by_gradient("#0000FF", "#00FF00") 
        
        # New explicit course launch subtitle
        subtitle = Text("Course Launch: SciML for Quant Finance", font_size=32, color=WHITE).next_to(title, DOWN)
        
        features = VGroup(
            Text("• Physics-Informed NNs", font_size=20, color=LIGHT_GREY),
            Text("• Deep BSDE Solvers", font_size=20, color=LIGHT_GREY),
            Text("• Neural SDEs & Deep Hedging", font_size=20, color=LIGHT_GREY)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(subtitle, DOWN, buff=0.5)

        with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
            d = tracker.duration
            self.play(Write(title), run_time=d * 0.2)
            self.play(FadeIn(subtitle, shift=UP*0.2), run_time=d * 0.2)
            self.play(FadeIn(features, shift=UP*0.1), run_time=d * 0.2)
            self.play(title.animate.scale(1.05), run_time=d * 0.3, rate_func=there_and_back)
            self.wait(d * 0.1)
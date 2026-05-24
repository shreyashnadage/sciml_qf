from manim import *
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_template import BaseTemplateScene

class SplitScene(BaseTemplateScene):
    def construct(self):
        config = self.scene_config
        text = config.get("voiceover", "")
        audio_kwargs = {}
        if "audio_path" in config:
            audio_kwargs["path"] = os.path.basename(config["audio_path"])
            
        layout = config.get("layout", "code_left_anim_right")
        
        # We will only render the code portion here for simplicity of the template.
        # Ideally, we would embed a pre-rendered animation as an ImageMobject sequence or movie.
        # But Manim Community supports VideoMobject! We can play a video on the right.
        
        # Check what's on the left
        left_config = config.get("left", {})
        if left_config.get("content") == "code":
            code_file_path = os.path.join(config["module_dir"], left_config.get("code_file", ""))
            line_range = left_config.get("code_range", [1, 20])
            
            with open(code_file_path, 'r') as f:
                lines = f.readlines()
            
            start_line = line_range[0] - 1
            end_line = line_range[1]
            subset_lines = lines[start_line:end_line]
            code_str = "".join(subset_lines)
            
            code_block = Code(
                code_string=code_str,
                tab_width=4,
                background="window",
                language="python",
                formatter_style="monokai",
                line_numbers_from=line_range[0],
                paragraph_config={"font_size": 14}
            ).scale(0.7)
            code_block.to_edge(LEFT, buff=0.5)
            
        divider = Line(UP*3.5, DOWN*3.5, color=GREY_D)
        
        # Right side placeholder
        placeholder = Text("Animation Area", color=GREY).to_edge(RIGHT, buff=2)
        
        with self.voiceover(text=text, **audio_kwargs) as tracker:
            self.play(FadeIn(code_block), Create(divider), FadeIn(placeholder))
            self.wait(tracker.duration)
            
        self.play(FadeOut(code_block), FadeOut(divider), FadeOut(placeholder))

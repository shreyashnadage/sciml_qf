from manim import *
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_template import BaseTemplateScene

class CodeScene(BaseTemplateScene):
    def construct(self):
        config = self.scene_config
        
        # Ensure path to code file is absolute
        code_file_path = os.path.join(config["module_dir"], config["code_file"])
        
        with open(code_file_path, 'r') as f:
            lines = f.readlines()
            
        line_range = config.get("code_range", [1, 20])
        
        # line_range is 1-indexed
        start_line = line_range[0] - 1
        end_line = line_range[1]
        subset_lines = lines[start_line:end_line]
        code_str = "".join(subset_lines)
        
        # Load the code block
        code_block = Code(
            code_string=code_str,
            tab_width=4,
            background="window",
            language="python",
            formatter_style="monokai",
            add_line_numbers=True,
            paragraph_config={"font_size": 16}
        ).scale(0.8)
        
        # In Manim, line numbers start from 1, but the `Code` object's `.code` attribute 
        # is a VGroup of lines where index 0 corresponds to the first line in the file.
        # Since we use insert_line_no=True, the code lines are actually VGroups of (line_no, line_text).
        
        text = config.get("voiceover", "")
        # Force the audio path since we pre-generated it
        audio_kwargs = {}
        if "audio_path" in config:
            # Tell the service to bypass generation and use this path
            # QwenSpeechService checks cache first, but we can force path
            audio_kwargs["path"] = os.path.basename(config["audio_path"])
        
        with self.voiceover(text=text, **audio_kwargs) as tracker:
            self.play(FadeIn(code_block), run_time=1)
            
            # Perform highlights
            highlights = config.get("highlights", [])
            for highlight in highlights:
                # In the YAML, lines are 1-indexed relative to the whole file
                # But our code block only contains a subset.
                # So we must map to the subset index (0-indexed).
                hl_start = highlight["lines"][0] - line_range[0]
                hl_end = highlight["lines"][-1] - line_range[0]
                
                # Check bounds
                if hl_start < 0 or hl_end >= len(code_block.code_lines):
                    continue
                
                # Highlight block
                lines_to_highlight = code_block.code_lines[hl_start : hl_end + 1]
                highlight_rect = SurroundingRectangle(
                    lines_to_highlight,
                    color=YELLOW, buff=0.1, fill_opacity=0.2
                )
                
                self.play(Create(highlight_rect), run_time=0.5)
                self.wait(highlight.get("pause", 1.0))
                self.play(FadeOut(highlight_rect), run_time=0.3)
            
            # Wait out the rest of the voiceover
            self.wait(tracker.duration)
        
        self.play(FadeOut(code_block), run_time=0.5)

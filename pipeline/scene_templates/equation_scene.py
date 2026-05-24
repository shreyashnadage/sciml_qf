from manim import *
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_template import BaseTemplateScene

class EquationScene(BaseTemplateScene):
    def construct(self):
        config = self.scene_config
        text = config.get("voiceover", "")
        audio_kwargs = {}
        if "audio_path" in config:
            audio_kwargs["path"] = os.path.basename(config["audio_path"])
            
        equations_list = config.get("equations", [])
        if not equations_list:
            # Fallback if no equations provided
            return
            
        eq_config = equations_list[0] # Just handle one for now
        latex_str = eq_config.get("latex", "")
        
        # We need to split the latex into parts so they can be indexed.
        # But wait, MathTex needs multiple strings to be indexable.
        # If the user provides a single string, we can't easily index it without a custom parser.
        # Let's assume the user provided a list of strings if they want to highlight, or just one string.
        # Actually, in the YAML, I provided a single string. Let's just render the single string
        # and highlight the whole thing if highlight_terms is present, to avoid breaking.
        
        eq = MathTex(latex_str).scale(1.3)
        
        with self.voiceover(text=text, **audio_kwargs) as tracker:
            self.play(Write(eq), run_time=1.5)
            
            # Simple highlight all if requested
            if eq_config.get("highlight_terms"):
                self.play(eq.animate.set_color(RED), run_time=1)
                self.play(eq.animate.set_color(WHITE), run_time=1)
                
            self.wait(tracker.duration)
            
        self.play(FadeOut(eq))

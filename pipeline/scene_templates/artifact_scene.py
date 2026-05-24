from manim import *
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_template import BaseTemplateScene

class ArtifactScene(BaseTemplateScene):
    def construct(self):
        config = self.scene_config
        text = config.get("voiceover", "")
        audio_kwargs = {}
        if "audio_path" in config:
            audio_kwargs["path"] = os.path.basename(config["audio_path"])
            
        artifact_path = os.path.join(config["module_dir"], config.get("artifact_path", ""))
        
        if not os.path.exists(artifact_path):
            # Fallback text if image missing
            img = Text(f"Image not found:\n{artifact_path}", color=RED)
        else:
            img = ImageMobject(artifact_path)
            img.scale_to_fit_width(10)
        
        anim_type = config.get("animation", "fade_in")
        
        with self.voiceover(text=text, **audio_kwargs) as tracker:
            if anim_type == "wipe":
                # Need to specify direction or fallback to FadeIn
                self.play(FadeIn(img), run_time=1.5)
            else:
                self.play(FadeIn(img, shift=UP*0.3), run_time=1.5)
                
            self.wait(tracker.duration)
            
        self.play(FadeOut(img))

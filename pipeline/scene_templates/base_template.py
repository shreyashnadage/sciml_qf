import os
import json
from manim import *
from manim_voiceover import VoiceoverScene
import sys

# Ensure qwen_voiceover can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from qwen_voiceover import QwenSpeechService

class BaseTemplateScene(VoiceoverScene):
    def setup(self):
        # Load the configuration passed by director.py
        config_path = os.environ.get("SCENE_CONFIG_PATH")
        if not config_path or not os.path.exists(config_path):
            raise ValueError("SCENE_CONFIG_PATH not set or file not found.")
            
        with open(config_path, "r") as f:
            self.scene_config = json.load(f)
            
        # We also need to set up the speech service.
        # Since audio is pre-generated, the speech service doesn't need to do generation,
        # but manim-voiceover still requires it for the context manager.
        # However, QwenSpeechService checks for cache_dir and file existence.
        
        # It's better to just use a dummy or the real QwenSpeechService with the audio path.
        # Let's set it up using QwenSpeechService.
        media_dir = os.path.join(self.scene_config["module_dir"], "media", "voiceovers")
        speaker = self.scene_config.get("global_config", {}).get("voice", {}).get("speaker", "Ryan")
        
        self.set_speech_service(
            QwenSpeechService(
                speaker=speaker,
                cache_dir=media_dir
            )
        )

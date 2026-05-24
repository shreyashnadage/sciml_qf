from manim_voiceover.services.base import SpeechService
from pathlib import Path
import os
import sys
import subprocess

class QwenSpeechService(SpeechService):
    audio_extension = ".mp3"
    
    def __init__(
        self, 
        model_path="Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", 
        speaker="Ryan", 
        language="English",
        **kwargs
    ):
        self.model_path = model_path
        self.speaker = speaker
        self.language = language
        # We don't load the model here! The subprocess will do it.
        super().__init__(**kwargs)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        # 1. Determine the filename
        if path is not None:
            audio_path = Path(path).name
        else:
            # Use the helper to get a hash-based filename
            audio_path = self.get_audio_basename({"input_text": text, **kwargs}) + ".wav"

        # 2. Use self.cache_dir if cache_dir argument is None
        actual_cache_dir = cache_dir if cache_dir is not None else self.cache_dir
        full_path = Path(actual_cache_dir) / audio_path
        
        # Ensure the directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 3. Save to the path as MP3 (preferred by manim-voiceover)
        if audio_path.endswith(".wav"):
             audio_path = audio_path[:-4] + ".mp3"
        
        mp3_full_path = full_path.with_suffix(".mp3")
        
        # Check if the audio file is already cached
        if mp3_full_path.exists() and mp3_full_path.stat().st_size > 0:
            print(f"Cache hit: {mp3_full_path} already exists. Skipping TTS generation.")
            return {"original_audio": audio_path}
        
        # The 'instruct' parameter allows adding emotions/styles
        instruct = kwargs.get("instruct", "Professional and clear educational tone.")
        
        # 4. Run the subprocess to generate the TTS
        worker_script = Path(__file__).parent / "qwen_tts_worker.py"
        python_exe = sys.executable
        
        print(f"Generating TTS for: {text[:30]}...")
        result = subprocess.run([
            python_exe, str(worker_script),
            "--text", text,
            "--output_mp3", str(mp3_full_path),
            "--instruct", instruct
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"TTS Worker failed with code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            raise RuntimeError("TTS generation failed")
            
        # 5. Return the relative path in a dict
        return {"original_audio": audio_path}

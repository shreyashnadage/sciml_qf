import sys
import os
import soundfile as sf
import torch
import argparse
from pathlib import Path

# Add parent dir to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from qwen_tts import Qwen3TTSModel

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--output_mp3", required=True)
    parser.add_argument("--instruct", default="Professional and clear educational tone.")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print("Initializing Qwen3TTSModel in subprocess...")
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        device_map=device,
        dtype=torch.bfloat16 if device == "cuda" else torch.float32,
        attn_implementation="sdpa" if device == "cuda" else "eager",
    )
    
    print("Generating voice...")
    wavs, sr = model.generate_custom_voice(
        text=args.text,
        language="English",
        speaker="Ryan",
        instruct=args.instruct
    )
    
    output_path = Path(args.output_mp3)
    wav_path = output_path.with_suffix(".wav")
    
    sf.write(str(wav_path), wavs[0], sr)
    
    print("Converting to MP3...")
    os.system(f'ffmpeg -y -i "{wav_path}" "{output_path}" -loglevel quiet')
    
    if os.path.exists(wav_path):
        os.remove(wav_path)
        
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    main()

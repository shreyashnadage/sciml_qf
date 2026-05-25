import os
import sys
import yaml
import json
import argparse
import subprocess
import hashlib
import shutil
from pathlib import Path

# Ensure we can import qwen_voiceover
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qwen_voiceover import QwenSpeechService

def get_video_duration(path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0

def mux_audio_to_video(video_path, audio_path):
    print(f"    -> Multiplexing audio for {video_path.name}...")
    temp_video = video_path.with_name(f"temp_{video_path.name}")
    
    cmd = [
        "ffmpeg", "-y", 
        "-i", str(video_path), 
        "-i", str(audio_path), 
        "-c:v", "copy", 
        "-c:a", "aac", 
        "-map", "0:v:0", 
        "-map", "1:a:0?", 
        str(temp_video)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and temp_video.exists():
        temp_video.replace(video_path)
    else:
        print(f"Warning: Failed to mux audio for {video_path.name}. FFmpeg error:\n{result.stderr}")

def parse_args():
    parser = argparse.ArgumentParser(description="SciML QF Video Director")
    parser.add_argument("module_dir", help="Path to the module directory (e.g. 02_physics_of_no_arbitrage)")
    parser.add_argument("--phase", choices=["audio", "render", "video", "stitch", "all"], default="all")
    parser.add_argument("--quality", choices=["l", "m", "h", "k"], default="l", help="Manim quality flag")
    parser.add_argument("--scene", default=None, help="Only process this specific scene ID")
    return parser.parse_args()

def load_script(module_dir):
    # Try director_scripts folder first, then fallback to module root
    script_path = Path(module_dir) / "director_scripts" / "script.yaml"
    if not script_path.exists():
        script_path = Path(module_dir) / "script.yaml"
        
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found in {module_dir} or {module_dir}/director_scripts")
    with open(script_path, "r") as f:
        return yaml.safe_load(f)

def get_audio_filename(scene, script):
    scene_id = scene.get("id")
    if not scene_id:
        return None
    text = scene.get("voiceover", "").strip()
    if not text:
        return None
        
    voice_config = script.get("voice", {})
    speaker = voice_config.get("speaker", "Ryan").strip()
    default_instruct = voice_config.get("default_instruct", "Professional, educational, measured pace.").strip()
    instruct = scene.get("instruct", default_instruct).strip()
    
    # Normalize text representation to ignore whitespace/newline differences
    normalized_text = " ".join(text.split())
    
    # Create unique string representation for hashing
    hash_payload = f"text:{normalized_text}|speaker:{speaker}|instruct:{instruct}"
    hash_digest = hashlib.md5(hash_payload.encode('utf-8')).hexdigest()
    
    return f"{scene_id}_{hash_digest}.mp3"

def archive_old_audio_files(media_dir, scene_id, current_audio_name):
    archive_dir = media_dir / "archive"
    for p in media_dir.glob(f"{scene_id}_*.mp3"):
        if p.name != current_audio_name:
            print(f"Archiving old voiceover file: {p.name} -> archive/")
            archive_dir.mkdir(parents=True, exist_ok=True)
            try:
                dest_path = archive_dir / p.name
                shutil.move(str(p), str(dest_path))
            except Exception as e:
                print(f"Error archiving {p.name}: {e}")

def generate_audio(script, module_dir, scene_id=None):
    print("=== PHASE 1: GENERATING AUDIO ===")
    media_dir = Path(module_dir) / "media" / "voiceovers"
    media_dir.mkdir(parents=True, exist_ok=True)
    
    voice_config = script.get("voice", {})
    speaker = voice_config.get("speaker", "Ryan")
    
    service = QwenSpeechService(speaker=speaker, cache_dir=str(media_dir))
    
    scenes = script.get("scenes", [])
    if scene_id:
        scenes = [s for s in scenes if s.get("id") == scene_id]
        if not scenes:
            print(f"Scene '{scene_id}' not found in script.")
            return
            
    # Determine how many scenes actually require voiceover generation
    audio_scenes = [s for s in scenes if get_audio_filename(s, script)]
    total_audio = len(audio_scenes)
    
    print(f"Total voiceover clips to process: {total_audio}")
    
    current_count = 0
    for scene in scenes:
        audio_name = get_audio_filename(scene, script)
        if not audio_name:
            continue
            
        current_count += 1
        print(f"[{current_count}/{total_audio}] Checking/generating voiceover for scene '{scene['id']}' ({audio_name})...")
        
        archive_old_audio_files(media_dir, scene["id"], audio_name)
        
        text = scene.get("voiceover", "")
        normalized_text = " ".join(text.split())
        default_instruct = voice_config.get("default_instruct", "Professional, educational, measured pace.")
        instruct = scene.get("instruct", default_instruct)
        
        try:
            service.generate_from_text(normalized_text, path=audio_name, instruct=instruct)
            # Add the generated audio path to the scene config for rendering
            scene["audio_path"] = str(media_dir / audio_name)
            print(f"[{current_count}/{total_audio}] Completed voiceover for scene '{scene['id']}'")
        except Exception as e:
            print(f"[{current_count}/{total_audio}] Error generating audio for {scene['id']}: {e}")

def render_scenes(script, module_dir, quality, scene_id=None):
    print(f"=== PHASE 2: RENDERING SCENES (Quality: -q{quality}) ===")
    pipeline_dir = Path(__file__).parent.resolve()
    
    # Ensure a consistent output directory for the module
    manim_output_dir = Path(module_dir).resolve() / "media" / "videos"
    
    scenes = script.get("scenes", [])
    if scene_id:
        scenes = [s for s in scenes if s.get("id") == scene_id]
        if not scenes:
            print(f"Scene '{scene_id}' not found in script.")
            return
            
    total_scenes = len(scenes)
    
    print(f"Total video clips to render: {total_scenes}")
    
    for idx, scene in enumerate(scenes, 1):
        print(f"[{idx}/{total_scenes}] Rendering video scene '{scene['id']}' ({scene['type']})...")
        
        # Save scene config to a temporary file for the templates to read
        scene_config_path = pipeline_dir / ".current_scene.json"
        
        # We need to make sure paths in the config are absolute so the template can find them
        # if the template is run from a different cwd. We will run manim from the module_dir.
        scene_full = dict(scene)
        
        # Compute exact hashed audio path if voiceover exists
        audio_name = get_audio_filename(scene, script)
        if audio_name:
            media_dir = Path(module_dir).resolve() / "media" / "voiceovers"
            scene_full["audio_path"] = str(media_dir / audio_name)
            
        scene_full["module_dir"] = str(Path(module_dir).resolve())
        scene_full["global_config"] = {
            "fps": script.get("fps", 30),
            "resolution": script.get("resolution", "1920x1080"),
            "voice": script.get("voice", {})
        }
        
        with open(scene_config_path, "w") as f:
            json.dump(scene_full, f)
            
        scene_type = scene.get("type", "animation")
        
        if scene_type == "animation":
            # For pure animations, we use the user's source file
            source_file = scene.get("source", "scenes.py")
            if not Path(source_file).is_absolute():
                # Assume it's in the manim/ directory of the module
                source_file = Path(module_dir).resolve() / "manim" / source_file
            manim_class = scene.get("manim_class")
            
        else:
            # For template scenes, we use our pipeline templates
            source_file = pipeline_dir / "scene_templates" / f"{scene_type}_scene.py"
            manim_class = f"{scene_type.capitalize()}Scene"
            
        if not Path(source_file).exists():
            print(f"[{idx}/{total_scenes}] Error: Source file {source_file} does not exist.")
            continue
            
        # Run manim
        # We run it with the module_dir as CWD so relative paths in user code work
        # Also set media_dir to the module's media dir
        cmd = [
            sys.executable, "-m", "manim", 
            f"-q{quality}", 
            str(source_file), manim_class,
            "--media_dir", str(Path(module_dir).resolve() / "media")
        ]
        
        # Pass the config path via environment variable
        env = os.environ.copy()
        env["SCENE_CONFIG_PATH"] = str(scene_config_path)
        
        # Use our sox path for Windows if present
        env["PATH"] = env.get("PATH", "") + ";C:\\Program Files (x86)\\sox-14-4-2"
        
        result = subprocess.run(cmd, cwd=str(Path(module_dir).resolve()), env=env)
        
        if result.returncode != 0:
            print(f"Failed to render scene {scene['id']}")
            sys.exit(1)
            
        print(f"[{idx}/{total_scenes}] Finished rendering video scene '{scene['id']}'")
        
        # Multiplex audio if we have it
        q_map = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}
        videos_dir = Path(module_dir).resolve() / "media" / "videos"
        
        rendered_video = None
        for p in videos_dir.rglob(f"{manim_class}.mp4"):
            if q_map[quality] in str(p):
                rendered_video = p
                break
        if not rendered_video:
            matches = list(videos_dir.rglob(f"{manim_class}.mp4"))
            if matches:
                rendered_video = matches[0]
                
        if rendered_video:
            # CREATE NEW DIRECTORY: Save the renamed copy to a dedicated clips folder
            clips_dir = Path(module_dir).resolve() / "media" / "scene_clips"
            clips_dir.mkdir(parents=True, exist_ok=True)
            
            scene_specific_video = clips_dir / f"{scene['id']}.mp4"
            
            try:
                shutil.copy(str(rendered_video), str(scene_specific_video))
                rendered_video = scene_specific_video
            except Exception as e:
                print(f"Warning: Failed to copy to scene-specific name: {e}")
                
            if audio_name:
                audio_path = Path(module_dir).resolve() / "media" / "voiceovers" / audio_name
                if audio_path.exists():
                    mux_audio_to_video(rendered_video, audio_path)

def stitch_video(script, module_dir, quality):
    print("=== PHASE 3: STITCHING VIDEO ===")
    
    q_map = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}
    
    videos_dir = Path(module_dir).resolve() / "media" / "videos"
    clips_dir = Path(module_dir).resolve() / "media" / "scene_clips"
    
    video_files = []
    
    for scene in script.get("scenes", []):
        scene_type = scene.get("type", "animation")
        if scene_type == "animation":
            source_name = Path(scene.get("source", "scenes.py")).stem
            manim_class = scene.get("manim_class")
        else:
            source_name = f"{scene_type}_scene"
            manim_class = f"{scene_type.capitalize()}Scene"
            
        found = False
        
        # 1. First try to find the scene-specific video in the NEW directory
        for p in clips_dir.rglob(f"{scene['id']}.mp4"):
            video_files.append(p)
            found = True
            break
                
        if not found:
            # 2. Fallback to raw class name search in the ORIGINAL directory
            for p in videos_dir.rglob(f"{manim_class}.mp4"):
                if q_map[quality] in str(p):
                    video_files.append(p)
                    found = True
                    break
        
        if not found:
            # Second fallback to the first class name match
            matches = list(videos_dir.rglob(f"{manim_class}.mp4"))
            if matches:
                video_files.append(matches[0])
                found = True
            else:
                print(f"Warning: Could not find output video for scene {scene['id']} ({manim_class})")
                
    if not video_files:
        print("No videos found to stitch.")
        return
        
    out_file = Path(module_dir) / "media" / "final" / f"final_{Path(module_dir).name}.mp4"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    transition_style = script.get("transition_style", "cut").lower()
    transition_duration = float(script.get("transition_duration", 0.5))

    if transition_style in ["crossfade", "fade"] and len(video_files) > 1:
        print(f"Applying crossfade transition ({transition_duration}s) between {len(video_files)} scenes...")
        
        inputs = []
        for vf in video_files:
            inputs.extend(["-i", str(vf)])
            
        v_filter = ""
        a_filter = ""
        
        current_len = get_video_duration(video_files[0])
        
        for i in range(1, len(video_files)):
            offset = current_len - transition_duration
            dur = get_video_duration(video_files[i])
            current_len = current_len + dur - transition_duration
            
            in_v1 = f"[{i-1}:v]" if i == 1 else f"[v{i-1}]"
            in_v2 = f"[{i}:v]"
            v_filter += f"{in_v1}{in_v2}xfade=transition=fade:duration={transition_duration}:offset={offset}[v{i}]; "
            
            in_a1 = f"[{i-1}:a]" if i == 1 else f"[a{i-1}]"
            in_a2 = f"[{i}:a]"
            a_filter += f"{in_a1}{in_a2}acrossfade=d={transition_duration}[a{i}]; "
            
        # Final filter strings
        v_filter = v_filter.strip()
        a_filter = a_filter.strip()
        filter_complex = f"{v_filter} {a_filter}"
        
        cmd = [
            "ffmpeg", "-y", 
            *inputs,
            "-filter_complex", filter_complex,
            "-map", f"[v{len(video_files)-1}]",
            "-map", f"[a{len(video_files)-1}]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            str(out_file)
        ]
        
        subprocess.run(cmd)
        print(f"Final video stitched and saved to: {out_file}")
        
    else:
        # Write ffmpeg concat file for standard cut
        concat_file = Path(module_dir) / "media" / "manifest.txt"
        with open(concat_file, "w") as f:
            for vf in video_files:
                path_str = str(vf).replace("\\", "/")
                f.write(f"file '{path_str}'\n")
                
        # Call ffmpeg
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
            "-i", str(concat_file), 
            "-c", "copy", 
            str(out_file)
        ]
        
        subprocess.run(cmd)
        print(f"Final video stitched and saved to: {out_file}")


def main():
    args = parse_args()
    module_dir = args.module_dir
    script = load_script(module_dir)
    
    if args.phase == "video":
        os.environ["SCIML_DUMMY_AUDIO"] = "1"
    
    if args.phase in ["audio", "all"]:
        generate_audio(script, module_dir, args.scene)
        
    if args.phase in ["render", "video", "all"]:
        render_scenes(script, module_dir, args.quality, args.scene)
        
    if args.phase in ["stitch", "all"]:
        stitch_video(script, module_dir, args.quality)

if __name__ == "__main__":
    main()
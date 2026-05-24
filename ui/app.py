import streamlit as st
import os
import sys
import yaml
import json
import subprocess
import time
from pathlib import Path
import traceback

# Import custom styling
try:
    from styles import get_custom_css
except ImportError:
    # Fallback if imported differently
    from ui.styles import get_custom_css

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="SciML Quant Video Suite",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Custom Style Sheets
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Define Core Workspace Root Path
WORKSPACE_ROOT = Path("d:/SCIML_QF").resolve()

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def find_modules():
    """Scan root workspace for video modules containing script.yaml."""
    modules = []
    if not WORKSPACE_ROOT.exists():
        return modules
        
    for item in WORKSPACE_ROOT.iterdir():
        if item.is_dir() and not item.name.startswith(".") and item.name not in ["__pycache__", "env", "pipeline", "templates", "ui", "Qwen3-TTS", "media", "plan"]:
            script_path_1 = item / "script.yaml"
            script_path_2 = item / "director_scripts" / "script.yaml"
            if script_path_1.exists() or script_path_2.exists():
                modules.append(item.name)
    return sorted(modules)

def load_module_script(module_name):
    """Load script.yaml and return its content and path."""
    base_dir = WORKSPACE_ROOT / module_name
    script_path = base_dir / "director_scripts" / "script.yaml"
    if not script_path.exists():
        script_path = base_dir / "script.yaml"
        
    if not script_path.exists():
        raise FileNotFoundError(f"Script YAML not found in {module_name}")
        
    with open(script_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data, script_path

def load_module_voiceover(module_name):
    """Load voiceover.md if it exists, otherwise return template content."""
    base_dir = WORKSPACE_ROOT / module_name
    vo_path = base_dir / "director_scripts" / "voiceover.md"
    if not vo_path.exists():
        vo_path = base_dir / "voiceover.md"
        
    if vo_path.exists():
        with open(vo_path, "r", encoding="utf-8") as f:
            return f.read(), vo_path
    return "", None

def save_yaml_script(data, path):
    """Safely save dictionary to YAML format, preserving ordering."""
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, indent=2, allow_unicode=True, default_flow_style=False)

def save_voiceover_script(content, path):
    """Safely save voiceover script to markdown file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def create_new_module(folder_name, title, voice_speaker, script_option, voiceover_option, uploaded_script=None, uploaded_voiceover=None):
    """Create directory structure and default templates for a new module."""
    module_dir = WORKSPACE_ROOT / folder_name
    if module_dir.exists():
        raise FileExistsError(f"Module folder '{folder_name}' already exists.")
        
    # 1. Create directory structure
    dirs_to_create = [
        module_dir,
        module_dir / "director_scripts",
        module_dir / "manim",
        module_dir / "code",
        module_dir / "media",
        module_dir / "media" / "voiceovers",
        module_dir / "media" / "videos",
        module_dir / "media" / "final"
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
        
    # 2. Setup script.yaml
    script_dest = module_dir / "director_scripts" / "script.yaml"
    if script_option == "Template" or not uploaded_script:
        template_path = WORKSPACE_ROOT / "templates" / "script_yaml_template.yaml"
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                script_data = yaml.safe_load(f)
            # Personalize template
            script_data["module"] = folder_name
            script_data["title"] = title
            if "voice" in script_data:
                script_data["voice"]["speaker"] = voice_speaker
            save_yaml_script(script_data, script_dest)
        else:
            # Fallback simple yaml
            simple_yaml = {
                "module": folder_name,
                "title": title,
                "resolution": "1920x1080",
                "fps": 30,
                "voice": {"speaker": voice_speaker, "default_instruct": "Professional, educational, measured pace."},
                "scenes": [
                    {
                        "id": "scene_1_intro",
                        "type": "animation",
                        "voiceover": "Welcome to this newly created SciML quantitative finance module.",
                        "instruct": "Engaging, professional.",
                        "manim_class": "Scene1_Intro",
                        "source": "scenes.py"
                    }
                ]
            }
            save_yaml_script(simple_yaml, script_dest)
    else:
        # Save uploaded yaml
        uploaded_data = yaml.safe_load(uploaded_script.getvalue().decode("utf-8"))
        uploaded_data["module"] = folder_name
        uploaded_data["title"] = title
        save_yaml_script(uploaded_data, script_dest)
        
    # 3. Setup voiceover.md
    vo_dest = module_dir / "director_scripts" / "voiceover.md"
    if voiceover_option == "Template" or not uploaded_voiceover:
        template_path = WORKSPACE_ROOT / "templates" / "voiceover_md_template.md"
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Replace placeholder text with new title
            content = content.replace("[Module Title]", title)
            content = content.replace("[Module Number]", folder_name)
            save_voiceover_script(content, vo_dest)
        else:
            default_vo = f"# Recording Script: {folder_name} – {title}\n\n**[SCENE 1_intro: Introduction title card]**\n\n**(Pacing: Engaging, professional)**\n\n[Spoken Text: \"Welcome to this newly created SciML quantitative finance module.\"]\n"
            save_voiceover_script(default_vo, vo_dest)
    else:
        # Save uploaded file
        save_voiceover_script(uploaded_voiceover.getvalue().decode("utf-8"), vo_dest)
        
    # 4. Setup default scenes.py in manim/
    scenes_dest = module_dir / "manim" / "scenes.py"
    default_manim_code = """from manim import *

class Scene1_Intro(Scene):
    def construct(self):
        # Premium dark background is automatically provided
        title = Text("SciML Quantitative Finance", color=BLUE_D).scale(1.1)
        subtitle = Text("Physics & Geometry of Derivatives", color=PURPLE_A).scale(0.7).next_to(title, DOWN)
        
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=1.0)
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=1.0)
"""
    with open(scenes_dest, "w", encoding="utf-8") as f:
        f.write(default_manim_code)
        
    # 5. Setup empty code/demo.py file
    demo_code_dest = module_dir / "code" / "demo.py"
    demo_code_dest.parent.mkdir(parents=True, exist_ok=True)
    with open(demo_code_dest, "w", encoding="utf-8") as f:
        f.write("# Put your model training or evaluation code here\nprint('SciML Quant Demo Loaded')\n")
        
    # 6. Create standard README.md inside module folder
    readme_dest = module_dir / "README.md"
    readme_content = f"# Module: {title}\n\nThis is a standard SciML video module container created via the Production Suite UI.\n\n### Directory Layout\n- `director_scripts/`: Configuration YAML & creative voiceover scripts.\n- `manim/`: Manim animation script files.\n- `code/`: Mathematical & Neural network code implementations.\n- `media/`: Process assets (voiceovers, intermediate render videos, final video).\n"
    with open(readme_dest, "w", encoding="utf-8") as f:
        f.write(readme_content)

def find_final_video(module_name):
    """Find stitched final video path if exists."""
    final_dir = WORKSPACE_ROOT / module_name / "media" / "final"
    if not final_dir.exists():
        return None
    matches = list(final_dir.glob("*.mp4"))
    if matches:
        return matches[0]
    return None

def find_scene_videos(module_name):
    """Find all intermediate scene videos."""
    videos_dir = WORKSPACE_ROOT / module_name / "media" / "videos"
    if not videos_dir.exists():
        return []
    # Recursively find all mp4 files under videos dir
    return sorted(list(videos_dir.rglob("*.mp4")), key=lambda p: p.name)

# ---------------------------------------------------------
# Sidebar Panel & State Initialization
# ---------------------------------------------------------

# Load available modules
module_list = find_modules()

# Initialize session states
if "selected_module" not in st.session_state:
    st.session_state.selected_module = module_list[0] if module_list else ""
if "script_data" not in st.session_state:
    st.session_state.script_data = None
if "script_path" not in st.session_state:
    st.session_state.script_path = None
if "voiceover_text" not in st.session_state:
    st.session_state.voiceover_text = ""
if "voiceover_path" not in st.session_state:
    st.session_state.voiceover_path = None
if "loaded_module_name" not in st.session_state:
    st.session_state.loaded_module_name = ""

# Sidebar Branding
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <span style="font-size: 3rem;">🎬</span>
        <h2 style="margin-top: 0.5rem; background: linear-gradient(90deg, #6366f1, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SciML Production</h2>
        <p style="color: #64748b; font-size: 0.85rem;">Super Sleek Manim & TTS Pipeline</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📁 Module Selector")
    
    if module_list:
        selected_mod = st.selectbox(
            "Active Production Module",
            options=module_list,
            index=module_list.index(st.session_state.selected_module) if st.session_state.selected_module in module_list else 0
        )
        st.session_state.selected_module = selected_mod
    else:
        st.warning("No modules detected. Go to 'Create Module' tab to start!")
        st.session_state.selected_module = ""
        
    st.markdown("---")
    st.markdown("### 🖥️ Workspace Information")
    st.code(f"Root: {WORKSPACE_ROOT}", language="text")
    if st.session_state.selected_module:
        active_path = WORKSPACE_ROOT / st.session_state.selected_module
        st.caption(f"Active Dir: {active_path.name}")
        
    st.markdown("---")
    st.markdown("### ⚙️ Quick Environment Checks")
    # Quick checks
    ffmpeg_check = "✅ FFmpeg Detected" if subprocess.run(["where", "ffmpeg"], capture_output=True).returncode == 0 else "❌ FFmpeg Missing"
    manim_check = "✅ Manim Detected" if subprocess.run([sys.executable, "-m", "manim", "--version"], capture_output=True).returncode == 0 else "❌ Manim Missing"
    st.caption(ffmpeg_check)
    st.caption(manim_check)

# ---------------------------------------------------------
# Load Active Module Script Data
# ---------------------------------------------------------
if st.session_state.selected_module and st.session_state.loaded_module_name != st.session_state.selected_module:
    try:
        data, path = load_module_script(st.session_state.selected_module)
        st.session_state.script_data = data
        st.session_state.script_path = path
        
        vo_text, vo_path = load_module_voiceover(st.session_state.selected_module)
        st.session_state.voiceover_text = vo_text
        st.session_state.voiceover_path = vo_path
        
        st.session_state.loaded_module_name = st.session_state.selected_module
    except Exception as e:
        st.error(f"Error loading module configurations: {e}")

# ---------------------------------------------------------
# Header Layout
# ---------------------------------------------------------
st.markdown(f"""
<div class="header-container">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <span class="badge badge-primary">MANIM VIDEO PIPELINE</span>
            <span class="badge badge-success">QWEN3-TTS VOICE SYNTHESIS</span>
            <h1 class="header-title">SciML Quantitative Video Suite</h1>
            <p class="header-subtitle">Build, render, and refine stunning mathematical and neural network physics animations</p>
        </div>
        <div style="text-align: right; color: #cbd5e1;">
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 2px;">ACTIVE WORKSPACE</p>
            <h3 style="margin: 0; font-weight: 700; color: #f8fafc;">{st.session_state.selected_module or 'No Module Loaded'}</h3>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Tabs Layout
# ---------------------------------------------------------
tab_edit, tab_code, tab_play, tab_run, tab_create = st.tabs([
    "📝 Edit Script & Voiceover", 
    "💻 Code Editor",
    "🎬 Playback & Media Player", 
    "🚀 Launch Render Pipeline", 
    "📁 Create New Module"
])

# ---------------------------------------------------------
# TAB 1: EDIT SCRIPT & VOICEOVER
# ---------------------------------------------------------
with tab_edit:
    if not st.session_state.selected_module or not st.session_state.script_data:
        st.info("Please create or select a module to load the interactive editors.")
    else:
        st.markdown("### ✏️ Interactive Pipeline Configuration")
        
        # Dual-column layouts for editing: YAML (left), Voiceover (right)
        col_yaml, col_voiceover = st.columns([1, 1])
        
        with col_yaml:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<h4>⚙️ Global Script Settings</h4>', unsafe_allow_html=True)
            
            script_data = st.session_state.script_data
            
            # Global config editors
            g_title = st.text_input("Module Video Title", value=script_data.get("title", ""))
            script_data["title"] = g_title
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                g_res = st.selectbox("Resolution Mode", options=["1920x1080", "1280x720", "3840x2160"], index=["1920x1080", "1280x720", "3840x2160"].index(script_data.get("resolution", "1920x1080")))
                script_data["resolution"] = g_res
            with col_g2:
                g_fps = st.selectbox("Target FPS", options=[15, 30, 60], index=[15, 30, 60].index(script_data.get("fps", 30)))
                script_data["fps"] = g_fps
                
            # Voice config
            voice_conf = script_data.get("voice", {})
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                v_speaker = st.selectbox("Voice Speaker", options=["Ryan", "Lilly", "Grace", "Liam"], index=["Ryan", "Lilly", "Grace", "Liam"].index(voice_conf.get("speaker", "Ryan")))
                voice_conf["speaker"] = v_speaker
            with col_v2:
                v_instruct = st.text_input("Default Pacing/Emotion Style", value=voice_conf.get("default_instruct", "Professional, educational, measured pace."))
                voice_conf["default_instruct"] = v_instruct
                
            script_data["voice"] = voice_conf
            
            # Transition config
            st.markdown("---")
            st.markdown("##### 🎞️ Final Assembly Transitions")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                t_opts = ["cut", "crossfade"]
                t_idx = t_opts.index(script_data.get("transition_style", "cut")) if script_data.get("transition_style", "cut") in t_opts else 0
                t_style = st.selectbox("Transition Style", options=t_opts, index=t_idx)
                script_data["transition_style"] = t_style
            with col_t2:
                t_dur = st.number_input("Transition Duration (s)", min_value=0.1, max_value=5.0, value=float(script_data.get("transition_duration", 0.5)), step=0.1)
                script_data["transition_duration"] = t_dur
            
            # Optional Background Music
            music_conf = script_data.get("music", {})
            music_enabled = st.checkbox("Include Background Music", value=bool(music_conf))
            if music_enabled:
                if not music_conf:
                    music_conf = {"file": "media/audio/background.mp3", "volume": 0.1}
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m_file = st.text_input("Music File Path", value=music_conf.get("file", "media/audio/background.mp3"))
                    music_conf["file"] = m_file
                with col_m2:
                    m_vol = st.slider("Music Volume (Relative)", min_value=0.0, max_value=1.0, value=music_conf.get("volume", 0.1), step=0.05)
                    music_conf["volume"] = m_vol
                script_data["music"] = music_conf
            else:
                if "music" in script_data:
                    del script_data["music"]
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Scene interactive list
            st.markdown("---")
            st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">'
                        '<h4>🎬 Scenes Timeline Editor</h4>'
                        '</div>', unsafe_allow_html=True)
            
            scenes = script_data.get("scenes", [])
            
            # Render scenes dynamically
            scenes_to_delete = []
            scenes_to_move_up = -1
            scenes_to_move_down = -1
            
            for idx, scene in enumerate(scenes):
                scene_id = scene.get("id", f"scene_{idx}")
                scene_type = scene.get("type", "animation")
                
                with st.expander(f"🎬 Scene {idx+1}: {scene_id} ({scene_type.upper()})", expanded=False):
                    col_sc1, col_sc2 = st.columns([3, 1])
                    with col_sc1:
                        new_sc_id = st.text_input(f"Scene ID", value=scene_id, key=f"sc_id_{idx}")
                        scene["id"] = new_sc_id
                        
                        new_sc_type = st.selectbox(f"Scene Type", options=["animation", "equation", "code", "split", "artifact"], index=["animation", "equation", "code", "split", "artifact"].index(scene_type), key=f"sc_type_{idx}")
                        scene["type"] = new_sc_type
                    with col_sc2:
                        st.write("")
                        st.write("")
                        # Order management
                        st.markdown('<div class="scene-control-btn-container">', unsafe_allow_html=True)
                        col_o1, col_o2, col_o3 = st.columns(3)
                        with col_o1:
                            if st.button("⬆️", key=f"sc_up_{idx}", help="Move Up"):
                                scenes_to_move_up = idx
                        with col_o2:
                            if st.button("⬇️", key=f"sc_down_{idx}", help="Move Down"):
                                scenes_to_move_down = idx
                        with col_o3:
                            if st.button("🗑️", key=f"sc_del_{idx}", help="Delete Scene"):
                                scenes_to_delete.append(idx)
                        st.markdown('</div>', unsafe_allow_html=True)
                                
                    # Spoken audio
                    new_vo = st.text_area("Voiceover script text", value=scene.get("voiceover", ""), key=f"sc_vo_{idx}", help="Exactly what the AI narrator will say for this shot.")
                    scene["voiceover"] = new_vo
                    
                    new_inst = st.text_input("TTS Instruct (optional)", value=scene.get("instruct", ""), key=f"sc_inst_{idx}", help="Specific emotion or pacing instruction for this scene only.")
                    if new_inst:
                        scene["instruct"] = new_inst
                    elif "instruct" in scene:
                        # Keep existing if it was empty, or delete if not specified
                        pass
                        
                    # Type specific configurations
                    st.markdown("---")
                    st.caption("🔧 Scene Visual Parameters")
                    
                    if new_sc_type == "animation":
                        a_class = st.text_input("Manim Python Class", value=scene.get("manim_class", "Scene1_Intro"), key=f"anim_class_{idx}")
                        a_source = st.text_input("Python Source File", value=scene.get("source", "scenes.py"), key=f"anim_src_{idx}")
                        scene["manim_class"] = a_class
                        scene["source"] = a_source
                        
                    elif new_sc_type == "equation":
                        eqs = scene.get("equations", [])
                        if not eqs:
                            eqs = [{"latex": "\\frac{\\partial V}{\\partial t} = 0", "highlight_terms": []}]
                            scene["equations"] = eqs
                            
                        # Edit equations
                        st.write("##### Equations (LaTeX)")
                        eq_to_remove = []
                        for eq_idx, eq in enumerate(eqs):
                            st.markdown(f"**Equation {eq_idx + 1}**")
                            col_eq1, col_eq2, col_eq3 = st.columns([3, 2, 1])
                            with col_eq1:
                                latex_val = st.text_input("LaTeX String", value=eq.get("latex", ""), key=f"eq_lat_{idx}_{eq_idx}")
                                eq["latex"] = latex_val
                            with col_eq2:
                                high_terms_str = st.text_input("Highlight Terms (e.g. 0,2)", value=",".join(map(str, eq.get("highlight_terms", []))), key=f"eq_high_{idx}_{eq_idx}")
                                # Convert comma string back to list of ints
                                try:
                                    eq["highlight_terms"] = [int(x.strip()) for x in high_terms_str.split(",") if x.strip().isdigit()]
                                except Exception:
                                    eq["highlight_terms"] = []
                            with col_eq3:
                                st.write("")
                                if st.button("❌", key=f"eq_del_{idx}_{eq_idx}"):
                                    eq_to_remove.append(eq_idx)
                                    
                        # Remove deleted equation
                        for r_eq in sorted(eq_to_remove, reverse=True):
                            eqs.pop(r_eq)
                            st.rerun()
                            
                        if st.button("➕ Add Equation", key=f"eq_add_{idx}"):
                            eqs.append({"latex": "", "highlight_terms": []})
                            st.rerun()
                            
                    elif new_sc_type == "code":
                        c_file = st.text_input("Code Source File Path", value=scene.get("code_file", "code/demo.py"), key=f"code_file_{idx}")
                        scene["code_file"] = c_file
                        
                        col_cr1, col_cr2 = st.columns(2)
                        cr = scene.get("code_range", [1, 20])
                        with col_cr1:
                            cr_start = st.number_input("Start Line", value=int(cr[0]), min_value=1, step=1, key=f"cr_s_{idx}")
                        with col_cr2:
                            cr_end = st.number_input("End Line", value=int(cr[1]), min_value=1, step=1, key=f"cr_e_{idx}")
                        scene["code_range"] = [int(cr_start), int(cr_end)]
                        
                        # Highlights in JSON
                        h_list = scene.get("highlights", [])
                        h_json = json.dumps(h_list, indent=2)
                        h_text = st.text_area("Syntax Highlights blocks (JSON format)", value=h_json, key=f"code_high_{idx}", help="List of highlights: e.g. [{'lines': [5, 10], 'pause': 2.0}]")
                        try:
                            scene["highlights"] = json.loads(h_text)
                        except Exception:
                            st.caption("⚠️ Invalid JSON highlight configuration.")
                            
                    elif new_sc_type == "split":
                        s_layout = st.selectbox("Split Layout", options=["code_left_anim_right", "anim_left_code_right"], index=["code_left_anim_right", "anim_left_code_right"].index(scene.get("layout", "code_left_anim_right")), key=f"split_lay_{idx}")
                        scene["layout"] = s_layout
                        
                        # Left and Right contents config as raw JSON helper to be extremely precise
                        left_c = scene.get("left", {"content": "code", "code_file": "code/demo.py", "code_range": [1, 10]})
                        right_c = scene.get("right", {"content": "animation", "manim_class": "Scene1_Intro", "source": "scenes.py"})
                        
                        st.markdown("**Left Panel Properties (JSON)**")
                        l_text = st.text_area("Left config", value=json.dumps(left_c, indent=2), key=f"split_left_{idx}")
                        st.markdown("**Right Panel Properties (JSON)**")
                        r_text = st.text_area("Right config", value=json.dumps(right_c, indent=2), key=f"split_right_{idx}")
                        try:
                            scene["left"] = json.loads(l_text)
                            scene["right"] = json.loads(r_text)
                        except Exception:
                            st.caption("⚠️ Invalid JSON panels configurations.")
                            
                    elif new_sc_type == "artifact":
                        a_path = st.text_input("Artifact Image Path", value=scene.get("artifact_path", "media/validation_plot.png"), key=f"art_path_{idx}")
                        scene["artifact_path"] = a_path
                        
                        a_anim = st.selectbox("Appearance Animation", options=["fade_in", "wipe", "none"], index=["fade_in", "wipe", "none"].index(scene.get("animation", "fade_in")), key=f"art_anim_{idx}")
                        scene["animation"] = a_anim

                    # Add Scene Production Buttons
                    st.markdown("---")
                    st.markdown("##### 🚀 Scene-Level Production")
                    col_act1, col_act2, col_act3 = st.columns(3)
                    
                    director_script_path = WORKSPACE_ROOT / "pipeline" / "director.py"
                    base_cmd = [
                        sys.executable,
                        str(director_script_path),
                        st.session_state.selected_module,
                        "--scene", scene_id
                    ]
                    
                    def run_scene_phase(phase_name, sid=scene_id, bcmd=base_cmd):
                        # Save script.yaml first to reflect UI updates
                        save_yaml_script(st.session_state.script_data, st.session_state.script_path)
                        cmd = bcmd + ["--phase", phase_name]
                        with st.spinner(f"Running phase '{phase_name}' for scene {sid}..."):
                            try:
                                process = subprocess.run(
                                    cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True,
                                    cwd=str(WORKSPACE_ROOT)
                                )
                                if process.returncode == 0:
                                    st.success(f"Success: {phase_name.capitalize()} completed for scene '{sid}'!")
                                else:
                                    st.error(f"Error running phase '{phase_name}' for scene '{sid}':\n{process.stdout}")
                            except Exception as ex:
                                st.error(f"Failed to launch process: {ex}")
                                
                    with col_act1:
                        if st.button("🎙️ Render Audio", key=f"btn_aud_{idx}"):
                            run_scene_phase("audio")
                    with col_act2:
                        if st.button("🎬 Render Video", key=f"btn_vid_{idx}"):
                            run_scene_phase("render")
                    with col_act3:
                        if st.button("🔗 Synthesize Scene", key=f"btn_syn_{idx}"):
                            run_scene_phase("all")
            
            # Handle list modification actions
            if scenes_to_delete:
                for d_idx in sorted(scenes_to_delete, reverse=True):
                    scenes.pop(d_idx)
                st.session_state.script_data["scenes"] = scenes
                st.rerun()
                
            if scenes_to_move_up != -1 and scenes_to_move_up > 0:
                idx = scenes_to_move_up
                scenes[idx], scenes[idx-1] = scenes[idx-1], scenes[idx]
                st.session_state.script_data["scenes"] = scenes
                st.rerun()
                
            if scenes_to_move_down != -1 and scenes_to_move_down < len(scenes) - 1:
                idx = scenes_to_move_down
                scenes[idx], scenes[idx+1] = scenes[idx+1], scenes[idx]
                st.session_state.script_data["scenes"] = scenes
                st.rerun()
                
            # Add Scene Button
            st.markdown("---")
            if st.button("➕ Add Scene to Timeline", key="add_scene_btn"):
                new_scene_template = {
                    "id": f"scene_{len(scenes) + 1}_new",
                    "type": "animation",
                    "voiceover": "Enter narration here.",
                    "instruct": "Professional.",
                    "manim_class": "Scene1_Intro",
                    "source": "scenes.py"
                }
                scenes.append(new_scene_template)
                st.session_state.script_data["scenes"] = scenes
                st.rerun()
                
            # Master Save Button
            st.markdown("---")
            st.markdown('<div class="sec-button">', unsafe_allow_html=True)
            col_save1, col_save2 = st.columns(2)
            with col_save1:
                if st.button("💾 Save script.yaml Configuration", key="save_script_btn"):
                    try:
                        save_yaml_script(st.session_state.script_data, st.session_state.script_path)
                        st.success(f"Successfully saved YAML script to {st.session_state.script_path.name}")
                    except Exception as ex:
                        st.error(f"Error saving YAML: {ex}")
            with col_save2:
                # Toggle for Raw YAML Editor
                show_raw_yaml = st.checkbox("Show Raw YAML Code Editor", value=False)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Advanced raw text YAML editing
            if show_raw_yaml:
                st.markdown("##### 💻 Raw script.yaml Editor")
                try:
                    yaml_raw_content = yaml.safe_dump(st.session_state.script_data, sort_keys=False, indent=2, allow_unicode=True, default_flow_style=False)
                except Exception:
                    yaml_raw_content = ""
                
                raw_edit_text = st.text_area("YAML Code block", value=yaml_raw_content, height=400)
                if st.button("Apply Raw YAML Edits", key="apply_raw_yaml"):
                    try:
                        parsed_yaml = yaml.safe_load(raw_edit_text)
                        if parsed_yaml and isinstance(parsed_yaml, dict):
                            st.session_state.script_data = parsed_yaml
                            save_yaml_script(parsed_yaml, st.session_state.script_path)
                            st.success("Parsed and successfully applied raw YAML changes!")
                            st.rerun()
                        else:
                            st.error("Error: YAML content must be a valid key-value mapping.")
                    except Exception as yaml_ex:
                        st.error(f"Invalid YAML Syntax: {yaml_ex}")
            
        with col_voiceover:
            st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown('<h4>🎙️ Creative Voiceover Script Editor</h4>', unsafe_allow_html=True)
            st.caption("Write and structure the recording scripts for your scenes. Follow standard voiceover script guidelines.")
            
            vo_path = st.session_state.voiceover_path
            
            if vo_path:
                vo_editor_text = st.text_area(
                    f"Markdown Editor ({vo_path.name})",
                    value=st.session_state.voiceover_text,
                    height=500,
                    key="voiceover_markdown_editor"
                )
                
                col_vo_act1, col_vo_act2 = st.columns([1, 1])
                with col_vo_act1:
                    if st.button("💾 Save Voiceover Script", key="save_vo_btn"):
                        try:
                            save_voiceover_script(vo_editor_text, vo_path)
                            st.session_state.voiceover_text = vo_editor_text
                            st.success(f"Voiceover script successfully saved to {vo_path.name}!")
                        except Exception as vo_ex:
                            st.error(f"Error saving Voiceover file: {vo_ex}")
                            
                with col_vo_act2:
                    show_vo_preview = st.checkbox("Show Formatted Preview", value=True)
                
                if show_vo_preview:
                    st.markdown("---")
                    st.markdown("##### 👁️ Previewing Narrator Script")
                    st.markdown(vo_editor_text)
            else:
                st.warning("No voiceover.md script found for this module. You can create one manually inside director_scripts/voiceover.md or recreate this module using the 'Create Module' tab.")
                
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: CODE EDITOR
# ---------------------------------------------------------
with tab_code:
    if not st.session_state.selected_module:
        st.info("Please select a module to load the Code Editor.")
    else:
        st.markdown(f"### 💻 Code Editor: {st.session_state.selected_module}")
        st.caption("Edit Manim Python animations and model code directly from the UI.")
        
        module_path = WORKSPACE_ROOT / st.session_state.selected_module
        py_files = list(module_path.rglob("*.py"))
        
        # Filter out __pycache__ and env directories
        py_files = [f for f in py_files if "env" not in f.parts and "__pycache__" not in f.parts]
        
        if not py_files:
            st.warning("No Python files found in this module.")
        else:
            # Dropdown to select file
            file_options = [f.relative_to(module_path).as_posix() for f in py_files]
            
            # Default to manim/scenes.py if exists, else first
            default_idx = 0
            if "manim/scenes.py" in file_options:
                default_idx = file_options.index("manim/scenes.py")
                
            selected_file_rel = st.selectbox("Select File to Edit", options=file_options, index=default_idx)
            selected_file_abs = module_path / selected_file_rel
            
            with open(selected_file_abs, "r", encoding="utf-8") as f:
                code_content = f.read()
                
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            new_code_content = st.text_area("Python Editor", value=code_content, height=600, key=f"code_edit_{selected_file_rel}")
            
            if st.button("💾 Save Code File", key="save_code_btn"):
                try:
                    with open(selected_file_abs, "w", encoding="utf-8") as f:
                        f.write(new_code_content)
                    st.success(f"Successfully saved {selected_file_rel}")
                except Exception as e:
                    st.error(f"Error saving code: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: PLAYBACK & MEDIA PLAYER
# ---------------------------------------------------------
with tab_play:
    if not st.session_state.selected_module:
        st.info("No active module selected.")
    else:
        st.markdown(f"### 🎬 Asset Player: {st.session_state.selected_module}")
        
        # Search for video files
        final_vid = find_final_video(st.session_state.selected_module)
        scene_vids = find_scene_videos(st.session_state.selected_module)
        
        col_f, col_s = st.columns([3, 2])
        
        with col_f:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<h4>👑 Final Assembly Stitched Video</h4>', unsafe_allow_html=True)
            
            if final_vid:
                st.caption(f"File Path: {final_vid.relative_to(WORKSPACE_ROOT)}")
                # Render video directly in web browser
                try:
                    with open(final_vid, "rb") as video_file:
                        video_bytes = video_file.read()
                    st.video(video_bytes)
                except Exception as playback_err:
                    st.error(f"Direct playback failed: {playback_err}. Try launching the pipeline to stitch or generate it.")
            else:
                st.warning("Stitched final video not found! Launch the production pipeline in 'All' or 'Stitch' mode to generate the stitched asset.")
                st.info("Ensure the output file exists at: "
                        f"`{st.session_state.selected_module}/media/final/final_{st.session_state.selected_module}.mp4`")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_s:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<h4>📦 Scene Renders Library</h4>', unsafe_allow_html=True)
            st.caption("Browse and review individual shot renders generated by Manim before full stitching.")
            
            if scene_vids:
                # Create a list for selection
                scene_vid_names = [v.relative_to(WORKSPACE_ROOT / st.session_state.selected_module / "media" / "videos") for v in scene_vids]
                selected_scene_idx = st.selectbox("Inspect Scene Video", options=range(len(scene_vids)), format_func=lambda idx: str(scene_vid_names[idx]))
                
                chosen_scene_vid = scene_vids[selected_scene_idx]
                st.markdown(f"**Selected:** `{chosen_scene_vid.name}`")
                
                try:
                    with open(chosen_scene_vid, "rb") as v_file:
                        v_bytes = v_file.read()
                    st.video(v_bytes)
                except Exception as scene_playback_err:
                    st.error(f"Scene playback failed: {scene_playback_err}")
            else:
                st.info("No individual scene videos detected. Render your scenes in 'Render' or 'All' modes first!")
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: LAUNCH RENDER PIPELINE
# ---------------------------------------------------------
with tab_run:
    if not st.session_state.selected_module:
        st.info("Please select a module to trigger the pipeline.")
    else:
        st.markdown(f"### 🚀 Launch Production Pipeline: {st.session_state.selected_module}")
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h4>⚙️ Pipeline execution controls</h4>', unsafe_allow_html=True)
        
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            run_mode = st.selectbox(
                "Execution Phase Mode",
                options=["all", "audio", "render", "stitch"],
                format_func=lambda opt: {
                    "all": "Full Pipeline (Audio + Render + Stitch)",
                    "audio": "Audio Synthesis Only (TTS)",
                    "render": "Manim Rendering Only",
                    "stitch": "FFmpeg Assembly / Stitch Only"
                }[opt],
                index=0,
                help="Select which components of the video pipeline to run."
            )
        with col_r2:
            quality_mode = st.selectbox(
                "Manim Quality Level",
                options=["l", "m", "h", "k"],
                format_func=lambda opt: {
                    "l": "Low (480p15) [-ql]",
                    "m": "Medium (720p30) [-qm]",
                    "h": "High (1080p60) [-qh]",
                    "k": "Ultra/4K (2160p60) [-qk]"
                }[opt],
                index=0,
                help="Low quality is highly recommended for quick editing feedback loop!"
            )
        with col_r3:
            st.write("")
            st.write("")
            trigger_pipeline = st.button("🔥 Run Video Generation Pipeline", use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Interactive live execution log area
        log_placeholder = st.empty()
        
        if trigger_pipeline:
            # Prepare arguments
            director_script_path = WORKSPACE_ROOT / "pipeline" / "director.py"
            
            # Formulate command list
            # We invoke sys.executable so we use the exact virtual environment's python bin
            cmd = [
                sys.executable,
                str(director_script_path),
                st.session_state.selected_module,
                "--phase", run_mode,
                "--quality", quality_mode
            ]
            
            # Setup logging container
            logs = "Initializing pipeline runner...\n"
            logs += f"Command: {' '.join(cmd)}\n"
            logs += "---------------------------------------------------------\n"
            
            log_placeholder.markdown(f"""
            <div class="terminal-container">
                <div class="terminal-header">
                    <span class="terminal-dot dot-red"></span>
                    <span class="terminal-dot dot-yellow"></span>
                    <span class="terminal-dot dot-green"></span>
                    <span class="terminal-title">LIVE RENDER PROCESS LOGS</span>
                </div>
                <div class="terminal-content">{logs}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Copy parent environment
            env = os.environ.copy()
            # Ensure FFmpeg is accessible. On Windows systems we make sure PATH is maintained.
            
            try:
                # Launch the director process and capture logs
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=str(WORKSPACE_ROOT),
                    env=env
                )
                
                # Stream logs line by line
                while True:
                    line = process.stdout.readline()
                    if line == '' and process.poll() is not None:
                        break
                    if line:
                        logs += line
                        
                        # Add a quick styling flag on common output headers
                        styled_logs = logs
                        styled_logs = styled_logs.replace("=== PHASE 1: GENERATING AUDIO ===", '<span class="log-success">=== PHASE 1: GENERATING AUDIO ===</span>')
                        styled_logs = styled_logs.replace("=== PHASE 2: RENDERING SCENES", '<span class="log-success">=== PHASE 2: RENDERING SCENES</span>')
                        styled_logs = styled_logs.replace("=== PHASE 3: STITCHING VIDEO ===", '<span class="log-success">=== PHASE 3: STITCHING VIDEO ===</span>')
                        styled_logs = styled_logs.replace("Failed to render scene", '<span class="log-error">Failed to render scene</span>')
                        styled_logs = styled_logs.replace("Error", '<span class="log-error">Error</span>')
                        
                        log_placeholder.markdown(f"""
                        <div class="terminal-container">
                            <div class="terminal-header">
                                <span class="terminal-dot dot-red"></span>
                                <span class="terminal-dot dot-yellow"></span>
                                <span class="terminal-dot dot-green"></span>
                                <span class="terminal-title">LIVE RENDER PROCESS LOGS</span>
                            </div>
                            <div class="terminal-content">{styled_logs}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(0.01) # smooth stream pacing
                
                # Check outcome code
                returncode = process.wait()
                if returncode == 0:
                    st.success("🎉 Video generation pipeline completed successfully! Go to the 'Playback' tab to review your final high-fidelity video asset.")
                else:
                    st.error(f"❌ Video generation pipeline failed with exit code {returncode}. Review logs above to resolve mathematical or layout syntax errors.")
            except Exception as cmd_err:
                st.error(f"Pipeline launch failed: {cmd_err}")
                st.code(traceback.format_exc(), language="python")

# ---------------------------------------------------------
# TAB 4: CREATE NEW MODULE
# ---------------------------------------------------------
with tab_create:
    st.markdown("### 📁 Create New Video Production Module")
    st.caption("This tool instantly generates the standardized folder layout, sets up YAML files, voiceover markdowns, default Manim python classes, and makes them ready for production.")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h4>🛠️ Module Generation Parameters</h4>', unsafe_allow_html=True)
    
    with st.form("create_module_form"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            c_folder = st.text_input(
                "Module Folder Name", 
                placeholder="e.g. 04_pinn_black_scholes",
                help="Ensure it has no spaces or special characters. Use a two-digit prefix followed by underscores for numbering consistency."
            )
        with col_c2:
            c_title = st.text_input(
                "Module Video Title", 
                placeholder="e.g. Physics-Informed Neural Networks for Black-Scholes",
                help="A reader-friendly display title for animations and logs."
            )
            
        c_speaker = st.selectbox(
            "Default Narrator Speaker", 
            options=["Ryan", "Lilly", "Grace", "Liam"], 
            index=0,
            help="Select the AI voice profile to load by default."
        )
        
        st.markdown("---")
        st.markdown("##### 📝 Initial Config Options")
        
        col_co1, col_co2 = st.columns(2)
        with col_co1:
            script_opt = st.radio(
                "script.yaml Initialization",
                options=["Template", "Upload Custom File"],
                index=0,
                help="Start with a standard YAML shot template or upload an existing YAML script."
            )
            uploaded_script = st.file_uploader("Upload script.yaml", type=["yaml", "yml"])
            
        with col_co2:
            vo_opt = st.radio(
                "voiceover.md Initialization",
                options=["Template", "Upload Custom File"],
                index=0,
                help="Start with a pre-formatted narrator script template or upload an existing markdown voiceover script."
            )
            uploaded_voiceover = st.file_uploader("Upload voiceover.md", type=["md", "txt"])
            
        st.write("")
        submit_create = st.form_submit_button("🔥 Initialize Video Module Structure")
        
    if submit_create:
        # Validate inputs
        if not c_folder or not c_title:
            st.error("Error: Module Folder Name and Video Title must be filled.")
        elif any(char in c_folder for char in [" ", "\\", "/", "*", "?", '"', "<", ">", "|", ":"]):
            st.error("Error: Folder Name cannot contain spaces or special Windows path characters.")
        else:
            try:
                create_new_module(
                    folder_name=c_folder,
                    title=c_title,
                    voice_speaker=c_speaker,
                    script_option=script_opt,
                    voiceover_option=vo_opt,
                    uploaded_script=uploaded_script,
                    uploaded_voiceover=uploaded_voiceover
                )
                st.success(f"🎉 Successfully initialized Module container: '{c_folder}'!")
                st.info("Folders created under workspace: `director_scripts`, `manim`, `code`, `media/voiceovers`, `media/videos`, `media/final`.")
                
                # Reset selected module and trigger reloading
                st.session_state.selected_module = c_folder
                st.session_state.loaded_module_name = "" # Force reload
                st.rerun()
            except Exception as create_err:
                st.error(f"Failed to create module folder: {create_err}")
                st.code(traceback.format_exc(), language="python")
                
    st.markdown('</div>', unsafe_allow_html=True)

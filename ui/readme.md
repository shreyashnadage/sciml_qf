# 🎬 SciML Video Production Suite UI

Welcome to the **SciML Video Production Suite**, a super sleek, high-fidelity Streamlit user interface built specifically for managing our mathematical and deep learning video pipeline. 

This UI acts as an immersive "Director's Control Panel" to orchestrate the generation of voiceovers via Qwen3-TTS and animations via Manim, assembling them into final stitched YouTube-ready video modules.

---

## 🌟 Key Features

1. **📁 Standardized Module Initialization**: 
   Instantly generate the canonical directory layout (`director_scripts`, `manim`, `code`, `media/voiceovers`, etc.) for new mathematical finance modules. Select from pre-made templates or upload your own files to bootstrap in seconds.
   
2. **📝 Form-Based Timeline & Scene Editor**:
   - Fully customizable global configurations (resolution, frame rate, speaker voice, pacing guides, and optional background music).
   - Render and edit scenes in a beautiful glassmorphic visual list.
   - Dynamic inputs tailored for each specific **Scene Type** (`animation`, `equation`, `code`, `split`, `artifact`) so you never have to remember complex YAML configurations.
   - Instantly reorder, add, or delete scenes using simple interactive controls.
   - **Scene-specific renders**: Render individual scene audio, video, or synthesize/mux them together directly from the scene expansion panel.
   
3. **💻 Built-in Workspace Code Editor**:
   - View and edit any Python script, YAML config, or Markdown file inside the current module workspace directly from the dashboard.
   - Save changes instantly to iterate on custom Manim scenes without leaving the UI.
   
4. **🎙️ Voiceover Script Sync & Preview**:
   - Edit the creative narration prose (`voiceover.md`) in a dedicated Markdown text area.
   - Render structured HTML previews directly on the UI for real-time proofreading.
   
5. **🚀 Subprocess Live-Streaming Terminal**:
   - Configure Manim Quality Levels from Low (`-ql` for fast feedback) to Ultra-HD 4K (`-qk`).
   - Launch execution with multiple selective modes (`All Phases`, `Audio Only`, `Render Only`, or `Stitch Only`).
   - Stream stdout and stderr logs in a retro cyber-terminal with live color-coded highlighting of phases and compilation events.
   
6. **🎬 Built-in Playback & Media Player**:
   - Review and play the final stitched video product directly inside the browser using standard video tags.
   - Browse and play individual scene renders (`media/videos/`) to review animations block-by-block.

---

## 🛠️ Installation & Setup

All code is fully isolated inside the `ui/` folder, referencing the main repository's video pipeline structure.

### 1. Prerequisites
Ensure you have the following installed in your shell:
- **Python 3.12+**
- **FFmpeg** (configured on system path)
- **Sox** (optional, for custom voiceover enhancements)

### 2. Dependencies Installation
Run the following pip command using the project's virtual environment:
```bash
# From workspace root:
./env/python -m pip install streamlit watchfiles pyyaml
```

### 3. Launching the App
Run the Streamlit application using the local environment's python module runner:
```bash
# Launch Streamlit server:
env\python.exe -m streamlit run ui/app.py
```

---

## 📁 Repository Structure
```text
SCIML_QF/
├── ui/
│   ├── app.py          # Main Streamlit dashboard application
│   ├── styles.py       # Custom dark-theme glassmorphism CSS
│   ├── readme.md       # Developer overview (this file)
│   └── userguide.md    # Detailed guide on writing scripts and animations
├── pipeline/
│   ├── director.py     # Subprocess manager for TTS, Manim, & FFmpeg
│   └── scene_templates/# Pre-configured equation, code, and split classes
└── templates/
    ├── script_yaml_template.yaml
    └── voiceover_md_template.md
```

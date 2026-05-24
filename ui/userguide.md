# 📖 SciML Content Creator's User Guide

This guide walks you through the entire workflow of writing, animating, and synthesizing high-fidelity video tutorials for Quantitative Finance and SciML using our **Video Production Suite**.

---

## 🚀 The Three-Step Workflow

Creating an educational video requires structuring two files simultaneously in the `director_scripts` folder of a module:
1. `voiceover.md`: The narrative prose script read by the AI voice speaker.
2. `script.yaml`: The machine-readable shot list that coordinates what is shown on screen in sync with the audio.

---

## 📁 Step 1: Initialize a New Module

1. Open the UI and select the **Create New Module** tab.
2. Enter a structured folder name (e.g. `04_pinn_black_scholes`). We recommend double-digit prefixes to keep modules chronologically ordered.
3. Enter the full friendly title (e.g. `Physics-Informed Neural Networks for Black-Scholes`).
4. Select **Template** for both YAML and Voiceover to automatically bootstrap with working examples.
5. Click **Initialize Video Module Structure**. The UI will set up the following folders:
   - `director_scripts/`: Houses `script.yaml` and `voiceover.md`.
   - `manim/`: Contains Python files where you define your animations.
   - `code/`: Contains actual PyTorch/Python files that can be embedded in your code scenes.
   - `media/`: Output directories for generated assets.

---

## 📝 Step 2: Structure Your Scenes

In the **Edit Script & Voiceover** tab, you can customize your scenes. Every scene has a **Type** that controls what Manim draws on screen. Here is how to configure each type:

### 1. `animation` (Pure Manim Scene)
Used to display custom mathematical geometric figures, vector fields, or 3D surfaces that you write in Python.
- **Parameters**:
  - **Manim Python Class**: The name of the `class` in your Python file (e.g., `Scene1_Intro`).
  - **Python Source File**: The script where that class is located. Defaults to `scenes.py` in the module's `manim/` folder.
- **Workflow**:
  - Add your scene class to `manim/scenes.py`.
  - Enter the matching class name in the YAML Scene Editor.

### 2. `equation` (LaTeX Formula Reveal)
Displays a centered mathematical equation, fading in elements and highlighting terms in sync with the audio.
- **Parameters**:
  - **LaTeX String**: Standard LaTeX notation. *(Double backslashes are required for symbols like `\frac` or `\sigma`, e.g., `\\frac{\\partial V}{\\partial t}`)*.
  - **Highlight Terms**: A comma-separated list of 0-indexed terms in the equation to highlight sequentially (e.g., `2` will highlight the third term of the formula).

### 3. `code` (Syntax-Highlighted Walkthrough)
Displays a sleek code block with a dark terminal skin, highlighting individual ranges of lines as you explain them.
- **Parameters**:
  - **Code Source File Path**: Relative path to the code file (e.g., `code/pinn_black_scholes.py`).
  - **Start & End Lines**: The range of lines to show on screen.
  - **Syntax Highlights (JSON)**: Define when and what lines to highlight.
    *Example:*
    ```json
    [
      {"lines": [2, 5], "pause": 2.0},
      {"lines": [10], "pause": 1.5}
    ]
    ```

### 4. `split` (Dual-Pane Code + Animation Layout)
Displays code on one side and a running Manim animation on the other. Ideal for showing a training loop while plotting the neural network's loss surface!
- **Parameters**:
  - **Split Layout**: Choice of `code_left_anim_right` or `anim_left_code_right`.
  - **Left / Right Config (JSON)**: Specify the component type (`code`, `animation`, `equation`) and its respective parameters in a mini JSON structure.

### 5. `artifact` (Static Plot/Image Embed)
Loads a pre-rendered image, plot, or visual graphic directly into the video frame.
- **Parameters**:
  - **Artifact Image Path**: Path to the PNG or JPG file.
  - **Appearance Animation**: Transition type (choice of `fade_in`, `wipe`, or `none`).

### Scene-Specific Actions & Custom Code Editing
Under each scene card in the editor list, you will find direct action buttons:
- **🎙️ Render Audio Only**: Immediately synthesize TTS audio for the selected scene text.
- **📹 Render Video Only**: Run Manim to render the video file for this individual scene.
- **🔗 Synthesize / Mux Audio**: Run FFmpeg to mux the generated voiceover audio directly into this scene's video file.

Additionally, you can switch to the **Code Editor** tab in the dashboard. This allows you to view and edit any workspace files (such as `manim/scenes.py` or your model training codes) directly from the browser and save them instantly to iterate on custom visuals.

---

## 🚀 Step 3: Run the Compilation Pipeline

Once your script is saved, navigate to the **Launch Render Pipeline** tab to compile the assets:

1. **Set Quality Level**:
   - ⚠️ **Crucial Hack**: Set the quality to **Low (480p15) [-ql]** during the editing process! Low-quality renders compile up to 10x faster and use minimal CPU.
   - Switch to **High (1080p60) [-qh]** or **Ultra/4K (2160p60) [-qk]** only when you are ready to render the final publication master.
2. **Select Phase Mode**:
   - `Audio Only`: Synthesizes voiceovers from the text in `script.yaml` using Qwen3-TTS.
   - `Render Only`: Compiles all Manim animations (and template equations/code shots) without merging them.
   - `Stitch Only`: Assembles all existing compiled MP4 shots into a single continuous video with background music.
   - `Full Pipeline`: Runs all three phases sequentially.
3. **Stream Progress**:
   - Click **Run Video Generation Pipeline**.
   - Watch the cyberpunk console. If a compiling error occurs in your Manim Python script, the console will print out the exact python traceback to help you debug.
4. **Playback**:
   - Once completed, open the **Playback** tab.
   - Inspect individual scene renders to make sure text fits on screen.
   - Play the completed final video, download it, and upload to YouTube!

---

## 🛠️ Troubleshooting & Tips

### 1. TTS Generation Fails
- Make sure that the character limits are respected in voiceovers.
- If your voice generator says "Failed", verify that the Qwen worker is active and not blocked by background CUDA processes.

### 2. LaTeX Rendering Errors
- Standard LaTeX characters must be escaped: use `\\` instead of `\` in the YAML text.
- If your LaTeX formula fails to compile, try testing it in a normal Markdown cell first to ensure there are no missing braces `{}` or math-mode syntax issues.

### 3. Missing Audio in Stitched Video
- If individual scene videos have voiceovers but the stitched video has no sound, make sure your FFmpeg installation supports audio encoding and that the output MP3 directories under `media/voiceovers/` are populated correctly.

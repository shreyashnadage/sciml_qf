# End-to-End Video Production Pipeline: Architecture Discussion

## The Vision

You (the director) hand me three things per module:

1. **A script** — scene-by-scene directions (like your existing `voiceover.md`)
2. **The demo code** — the Python being explained (like `pinn_black_scholes.py`)
3. **Reference Manim visuals** — existing animation scenes (like `scenes.py`)

I produce one final, stitched MP4 with synchronized voiceover, animated code displays, rendered plots, and Manim animations — all frame-perfectly aligned.

---

## The Core Problem

Your voiceover script describes **heterogeneous content types** that need to coexist in a single timeline:

| Scene Type | Example from Module 2 | What's Shown |
|---|---|---|
| **3D Animation** | Scene 1 — Data cloud shattering | ThreeDScene with camera rotation |
| **2D Equation** | Scene 3 — PDE appears in darkness | MathTex with highlighting |
| **Conceptual Animation** | Scene 4 — Heat diffusion metaphor | 2D plot morphing |
| **Code Walkthrough** | Scene 8 — "Welcome back to Colab" | Syntax-highlighted code with line focus |
| **Live Output** | Scene 10 — Training loss drops | Pre-rendered plot/artifact embedded |
| **Split Screen** | Scene 8 — "Manim left, code right" | Two viewports simultaneously |

The challenge is that Manim handles types 1-3 natively, but types 4-6 require a **code display system** and an **artifact embedding pipeline** that doesn't exist yet.

---

## Proposed Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                   DIRECTOR'S INPUT                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Script   │  │  Demo Code   │  │ Reference Scenes  │  │
│  │ (YAML)   │  │  (.py files) │  │ (.py manim)       │  │
│  └────┬─────┘  └──────┬───────┘  └────────┬──────────┘  │
└───────┼───────────────┼───────────────────┼─────────────┘
        │               │                   │
        ▼               ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              SCENE GENERATOR ENGINE                     │
│                                                         │
│  1. Parse script → scene manifest                       │
│  2. For each scene:                                     │
│     ├─ Generate TTS audio (subprocess worker)           │
│     ├─ Build Manim VoiceoverScene class                 │
│     └─ Render individual MP4                            │
│  3. Stitch all MP4s → final video                       │
└─────────────────────────────────────────────────────────┘
```

### The Script Format

Your current `voiceover.md` is already 80% there. I propose a **structured YAML** companion that maps 1:1 with your prose script but adds the machine-readable metadata I need:

```yaml
module: "02_physics_of_no_arbitrage"
title: "The Physics of No-Arbitrage"
resolution: "1920x1080"
fps: 30
voice:
  speaker: "Ryan"
  default_instruct: "Professional, educational, measured pace."

scenes:
  - id: "intro_data_cloud"
    type: animation          # Pure Manim animation
    voiceover: >
      In our last video, we proved that a neural network can learn 
      the exact shape of a financial derivative. But we cheated.
    instruct: "Reflective, setting up a confession."
    manim_class: "Scene1_EmptyRoom"
    source: "scenes.py"
    
  - id: "pde_reveal"
    type: equation            # MathTex focused
    voiceover: >
      The answer lies in treating financial mathematics not as a 
      statistical spreadsheet, but as the laws of physics.
    instruct: "Deliberate, reverent."
    equations:
      - latex: "\\frac{\\partial V}{\\partial t} + \\frac{1}{2}\\sigma^2 S^2 \\frac{\\partial^2 V}{\\partial S^2} + rS \\frac{\\partial V}{\\partial S} - rV = 0"
        highlight_terms: [2]   # 0-indexed, highlight the Gamma term
    
  - id: "code_walkthrough_domain"
    type: code                # Code display scene
    voiceover: >
      Welcome back to Colab. Notice we are not importing any analytical 
      Black-Scholes formulas. Instead of data, we need to give the network 
      a space to explore.
    instruct: "Guiding, technical but accessible."
    code_file: "pinn_black_scholes.py"
    code_range: [26, 43]      # Lines to display
    highlights:               # Sequential highlight steps
      - lines: [32, 33]       # requires_grad=True
        pause: 2              # seconds to hold
      - lines: [42]           # relu payoff
        pause: 1.5
    
  - id: "code_walkthrough_physics"
    type: code
    voiceover: >
      Here is where the magic happens. We write our custom physics 
      loss function.
    instruct: "Instructional, building to an aha moment."
    code_file: "pinn_black_scholes.py"
    code_range: [69, 93]
    highlights:
      - lines: [76, 77]       # autograd.grad dV/dt
        pause: 2
      - lines: [84, 85]       # d2V/dS2 (Gamma)
        pause: 2
      - lines: [90]           # PDE residual construction
        pause: 3
    
  - id: "split_code_and_animation"
    type: split               # Code left, animation right
    voiceover: >
      We define a domain: stock prices from nearly zero to 150, 
      and time from zero to 1 year.
    left:
      content: code
      code_file: "pinn_black_scholes.py"
      code_range: [26, 35]
    right:
      content: animation
      manim_class: "Scene4_DomainSampling"
      source: "scenes.py"
      
  - id: "training_output"
    type: artifact            # Show pre-rendered image/plot
    voiceover: >
      The loss drops. The network is learning the geometry of the 
      market purely by staring at the PDE.
    instruct: "Triumphant, amazed."
    artifact_path: "media/pinn_validation.png"
    animation: "fade_in"      # How to reveal the artifact
    
  - id: "surface_reveal"
    type: animation
    voiceover: >
      Without a single piece of historical data, our neural network 
      has discovered the exact Black-Scholes option surface.
    instruct: "Triumphant, amazed."
    manim_class: "Scene5_SanityCheckChallenge"
    source: "scenes.py"
```

> [!TIP]
> You keep writing your creative script in prose Markdown as you already do. The YAML is the "shot list" — a structured companion that tells the engine exactly what to render for each beat.

---

## Scene Type Implementations

### 1. `animation` — Pure Manim Scenes (Already Working)

These are your existing `VoiceoverScene` classes. The engine simply:
- Generates TTS via subprocess worker
- Renders `manim -qh scenes.py ClassName`
- Outputs an MP4 per scene

**No new work needed** — this is what we built and validated today.

### 2. `equation` — LaTeX/MathTex Display

A reusable template scene that:
- Takes LaTeX strings from the YAML
- Renders them with cinematic dark backgrounds
- Supports term-by-term highlighting with color transitions
- Syncs each reveal step to the voiceover duration

```python
class EquationScene(VoiceoverScene):
    """Reusable template for equation reveals."""
    def construct(self):
        config = self.scene_config  # Injected from YAML
        with self.voiceover(text=config["voiceover"], 
                           instruct=config["instruct"]) as tracker:
            eq = MathTex(*config["latex_parts"]).scale(1.3)
            self.play(Write(eq), run_time=tracker.duration * 0.6)
            for idx in config.get("highlight_terms", []):
                self.play(eq[idx].animate.set_color(RED))
            self.wait(tracker.duration * 0.2)
```

### 3. `code` — Syntax-Highlighted Code Display ⭐ (New)

This is the most important new capability. Manim has a built-in `Code` mobject that renders syntax-highlighted source code. We build a template that:

- Reads the specified lines from your actual Python file
- Displays them with a dark IDE-like background
- Animates **line-by-line highlighting** in sync with the voiceover
- Supports scrolling for long code blocks

```python
class CodeScene(VoiceoverScene):
    """Displays code with animated line highlighting."""
    def construct(self):
        config = self.scene_config
        
        # Extract the relevant lines from the source file
        code_block = Code(
            file_name=config["code_file"],
            tab_width=4,
            background="window",           # IDE-style frame
            language="python",
            font_size=18,
            line_range=config["code_range"],
            style="monokai"                 # Dark syntax theme
        ).scale(0.8)
        
        with self.voiceover(text=config["voiceover"],
                           instruct=config["instruct"]) as tracker:
            self.play(FadeIn(code_block), run_time=1)
            
            # Highlight specified lines sequentially
            for highlight in config["highlights"]:
                highlight_rect = SurroundingRectangle(
                    code_block.code[highlight["lines"][0]:highlight["lines"][-1]+1],
                    color=YELLOW, buff=0.05
                )
                self.play(Create(highlight_rect), run_time=0.5)
                self.wait(highlight["pause"])
                self.play(FadeOut(highlight_rect), run_time=0.3)
```

### 4. `split` — Dual-Pane Layout (Code + Animation)

This is the "Colab on the left, Manim on the right" layout from Scene 8 of your script:

```python
class SplitScene(VoiceoverScene):
    """Side-by-side code and animation."""
    def construct(self):
        # Left pane: Code
        code_block = Code(...).scale(0.55)
        code_block.to_edge(LEFT, buff=0.3)
        
        # Right pane: Animation viewport
        # We render the animation separately and embed as ImageMobject,
        # OR we build both sides in the same scene using VGroup positioning
        
        divider = Line(UP*3.5, DOWN*3.5, color=GREY_D)
        
        with self.voiceover(text=...) as tracker:
            self.play(FadeIn(code_block), Create(divider))
            # Run animation on the right side...
```

### 5. `artifact` — Embedding Pre-Rendered Plots/Images

For training curves, validation plots, or any output from your demo code:

```python
class ArtifactScene(VoiceoverScene):
    """Displays a pre-rendered image (plot, diagram, etc.)."""
    def construct(self):
        config = self.scene_config
        
        img = ImageMobject(config["artifact_path"])
        img.scale_to_fit_width(10)
        
        with self.voiceover(text=config["voiceover"],
                           instruct=config["instruct"]) as tracker:
            self.play(FadeIn(img, shift=UP*0.3), run_time=1.5)
            self.wait(tracker.duration - 1.5)
```

---

## The Production Pipeline

### Phase 1: Pre-Generation (Audio + Artifacts)

Before any Manim rendering, we pre-generate all expensive assets:

```
┌──────────────────────────────────────────────────┐
│  Phase 1: Pre-Generate                           │
│                                                  │
│  1. Parse script.yaml → list of scenes           │
│  2. For each scene:                              │
│     ├─ Call qwen_tts_worker.py (subprocess)      │
│     ├─ Cache MP3 to media/voiceovers/            │
│     └─ If type=artifact, run demo code to        │
│        generate the plot/image                   │
│                                                  │
│  Output: All audio + images cached locally       │
└──────────────────────────────────────────────────┘
```

### Phase 2: Scene Rendering

Each scene renders independently as its own MP4:

```
┌──────────────────────────────────────────────────┐
│  Phase 2: Render Scenes                          │
│                                                  │
│  For each scene in manifest:                     │
│    ├─ If type=animation → manim -qh scene.py     │
│    ├─ If type=code      → manim -qh code_tmpl.py │
│    ├─ If type=equation  → manim -qh eq_tmpl.py   │
│    ├─ If type=split     → manim -qh split_tmpl.py│
│    └─ If type=artifact  → manim -qh art_tmpl.py  │
│                                                  │
│  Output: scene_01.mp4, scene_02.mp4, ...         │
└──────────────────────────────────────────────────┘
```

### Phase 3: Final Assembly

Stitch all scene MP4s into one production video:

```
┌──────────────────────────────────────────────────┐
│  Phase 3: Stitch                                 │
│                                                  │
│  1. Generate ffmpeg concat manifest:             │
│     file 'scene_01.mp4'                          │
│     file 'scene_02.mp4'                          │
│     ...                                          │
│  2. Run: ffmpeg -f concat -i manifest.txt        │
│          -c copy final_module_02.mp4             │
│                                                  │
│  3. (Optional) Add intro/outro cards,            │
│     background music, fade transitions           │
│                                                  │
│  Output: final_module_02.mp4                     │
└──────────────────────────────────────────────────┘
```

---

## Proposed Directory Structure

```
SCIML_QF/
├── pipeline/                          # NEW: The production engine
│   ├── director.py                    # Main orchestrator script
│   ├── scene_templates/               # Reusable Manim templates
│   │   ├── code_scene.py              # Code display template
│   │   ├── equation_scene.py          # Equation template
│   │   ├── split_scene.py             # Split-screen template
│   │   ├── artifact_scene.py          # Image/plot template
│   │   └── transition_scene.py        # Fade/wipe transitions
│   └── utils/
│       ├── script_parser.py           # YAML → scene manifest
│       ├── code_extractor.py          # Extract line ranges from .py
│       └── stitcher.py                # ffmpeg concat wrapper
│
├── qwen_voiceover.py                  # TTS bridge (exists)
├── qwen_tts_worker.py                 # TTS subprocess (exists)
│
├── 02_physics_of_no_arbitrage/
│   ├── script.yaml                    # NEW: Machine-readable shot list
│   ├── code/
│   │   └── pinn_black_scholes.py      # Demo code (exists)
│   ├── manim/
│   │   └── scenes.py                  # Custom animations (exists)
│   └── media/
│       ├── voiceover/voiceover.md     # Prose script (exists)
│       ├── voiceovers/                # Cached TTS audio
│       ├── artifacts/                 # Pre-rendered plots
│       └── final/                     # Output video
│           └── module_02_final.mp4
```

---

## Key Design Decisions to Discuss

### 1. Script Format: YAML vs Enhanced Markdown?

**Option A — YAML** (recommended): Clean separation of creative content and technical metadata. You write prose in `voiceover.md`, I consume structure from `script.yaml`.

**Option B — Annotated Markdown**: Embed YAML frontmatter blocks directly in the `voiceover.md`. Keeps everything in one file but mixes concerns.

### 2. Code Display Strategy

**Option A — Manim's `Code` mobject** (recommended): Native, renders within the same scene, supports highlighting via `SurroundingRectangle`. Looks like a real IDE.

**Option B — Pre-rendered screenshots**: Take screenshots of VS Code / Colab, embed as `ImageMobject`. Visually authentic but static and hard to animate.

**Option C — Hybrid**: Use `Code` for line-by-line walkthrough, screenshots for "here's the full notebook" establishing shots.

### 3. Audio Caching Strategy

**Option A — Pre-generate all audio before rendering** (recommended): Run TTS for every scene's voiceover text in one batch pass. This means:
- TTS errors are caught early before expensive renders
- Audio durations are known in advance for timing calculations
- Manim can use cached audio without re-generating

**Option B — Generate inline during render**: Simpler code but slower iteration cycles and you can't preview audio separately.

### 4. Transitions Between Scenes

**Option A — Hard cuts**: Simple `ffmpeg concat`. Works fine for educational content.

**Option B — Manim-native transitions**: Each scene ends with a `FadeOut` and starts with a `FadeIn`. Slightly smoother.

**Option C — ffmpeg crossfades**: Post-process transitions during stitching. Most flexible but adds complexity.

### 5. Resolution and Quality Tiers

| Flag | Resolution | FPS | Use Case |
|---|---|---|---|
| `-ql` | 480p / 15fps | Quick preview, script timing validation |
| `-qm` | 720p / 30fps | Draft review with stakeholders |
| `-qh` | 1080p / 30fps | **Production render for YouTube** |
| `-qk` | 4K / 60fps | Premium / future-proofing |

---

## The Workflow (How We'd Actually Use This)

### Step 1: You Write
```
You create/update:
  - voiceover.md  (creative prose, pacing notes, scene descriptions)
  - script.yaml   (structured shot list with scene types, code ranges, etc.)
```

### Step 2: I Pre-Generate
```
I run:
  python pipeline/director.py 02_physics_of_no_arbitrage --phase audio
  
This generates all TTS clips and caches them.
You can listen and iterate on the voice before any rendering.
```

### Step 3: I Draft Render
```
I run:
  python pipeline/director.py 02_physics_of_no_arbitrage --phase render --quality low
  
This renders all scenes at 480p/15fps for quick review.
You watch, give feedback, I adjust.
```

### Step 4: I Production Render
```
I run:
  python pipeline/director.py 02_physics_of_no_arbitrage --phase all --quality high
  
This renders everything at 1080p/30fps and stitches the final video.
```

---

## What's Already Built vs. What's Needed

| Component | Status | Effort |
|---|---|---|
| Qwen TTS integration | ✅ Done | — |
| Subprocess TTS worker | ✅ Done | — |
| VoiceoverScene sync | ✅ Done | — |
| Module 2 animation scenes | ✅ Done | — |
| Module 2 demo code | ✅ Done | — |
| Module 2 voiceover script | ✅ Done | — |
| YAML script parser | 🔲 Needed | Small |
| Code display template | 🔲 Needed | Medium |
| Equation template | 🔲 Needed | Small |
| Split-screen template | 🔲 Needed | Medium |
| Artifact embed template | 🔲 Needed | Small |
| Director orchestrator | 🔲 Needed | Medium |
| ffmpeg stitcher | 🔲 Needed | Small |
| Transition system | 🔲 Needed | Small |

> [!IMPORTANT]
> The hardest piece is the **Code Display Template** — getting Manim's `Code` mobject to look genuinely premium (IDE-like background, smooth line highlighting, proper font scaling) takes careful tuning. Everything else is plumbing.

---

## Open Questions for You

1. **Do you want the code to "type out" character by character**, or appear in blocks and then highlight? Typing is cinematic but slow; block reveal is faster and more practical for dense code.

2. **Should the voiceover script and YAML be separate files or combined?** I lean toward separate — your prose script stays readable, the YAML stays parseable.

3. **Do you want background music?** If so, I can add a `music` field to the YAML and mix it during the stitch phase at a configurable volume.

4. **For the split-screen scenes** — do you want the code on the left and animation on the right (like a VS Code + preview layout), or flexible per scene?

5. **Should I generate SRT subtitle files** alongside the video? Manim-voiceover already produces `.srt` — we just need to merge them across scenes.

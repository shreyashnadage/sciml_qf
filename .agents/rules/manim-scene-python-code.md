---
trigger: model_decision
description: use these rules while creating or working with any manim scene code.
---



```markdown
# Manim SciML Scene Generation Rules

You are an expert Manim coding agent. When generating new Manim scenes for this project, you must strictly adhere to the following architectural patterns, imports, custom classes, and animation timing rules.

## 1. Required Imports and Path Configurations
Every script must include the following standard imports and the specific `sys.path` injection to load the custom voiceover service.

```python
from manim import *
import numpy as np
from scipy.stats import norm
import sys
import os
import json
from pathlib import Path
from manim_voiceover import VoiceoverScene

# Add the project root to sys.path to import qwen_voiceover
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from qwen_voiceover import QwenSpeechService

```

## 2. Custom Base Classes

Do **not** inherit directly from `Scene` or `ThreeDScene`. You must inherit from the custom wrapper classes `SciMLScene` (for 2D) or `SciMLThreeDScene` (for 3D).

If you are asked to generate the base classes themselves, they must include the `setup` method that parses `SCENE_CONFIG_PATH` from the environment, sets up fallback configurations, initializes `QwenSpeechService`, and defines the `voiceover_path` property.

*Reference Implementation for Base Classes:*

```python
class SciMLScene(VoiceoverScene):
    def setup(self):
        config_path = os.environ.get("SCENE_CONFIG_PATH")
        if not config_path or not os.path.exists(config_path):
            self.scene_config = {
                "id": "manual",
                "voiceover": "This is fallback voiceover text.",
                "module_dir": str(Path(__file__).resolve().parents[2]),
                "global_config": {"voice": {"speaker": "Ryan"}}
            }
        else:
            with open(config_path, "r") as f:
                self.scene_config = json.load(f)
                
        media_dir = os.path.join(self.scene_config.get("module_dir", "."), "media", "voiceovers")
        speaker = self.scene_config.get("global_config", {}).get("voice", {}).get("speaker", "Ryan")
        self.set_speech_service(QwenSpeechService(speaker=speaker, cache_dir=media_dir))

    @property
    def voiceover_path(self):
        if "audio_path" in self.scene_config:
            return os.path.basename(self.scene_config["audio_path"])
        return None

# SciMLThreeDScene follows the exact same setup but inherits from (ThreeDScene, VoiceoverScene)

```

## 3. Scene Construction and Branching Logic

Scenes are designed to be modular and driven by an external configuration JSON.

* **Scene ID Extraction:** Always extract the `scene_id` at the start of your logic: `scene_id = self.scene_config.get("id", "")`
* **Branching:** Use `if "keyword" in scene_id:` to execute specific sub-animations.
* **Fallback:** Always include an `else:` block containing a standalone version of the animation with hardcoded `.wait()` times for manual testing.

## 4. Voiceover Synchronization (CRITICAL)

Animations within a configured scene branch must be perfectly timed to the generated voiceover audio.

* Wrap your animations in a `with self.voiceover(...) as tracker:` block.
* Pass the configuration text and path: `text=self.scene_config["voiceover"], path=self.voiceover_path`.
* **Proportional Timing:** Use fractions of `tracker.duration` for your `run_time`. The sum of all `run_time` and `self.wait()` durations inside the block must equal roughly `1.0 * tracker.duration`.

*Example:*

```python
with self.voiceover(text=self.scene_config["voiceover"], path=self.voiceover_path) as tracker:
    self.play(Create(axes), run_time=tracker.duration * 0.4)
    self.play(Create(payoff), run_time=tracker.duration * 0.4)
    self.wait(tracker.duration * 0.2)

```

## 5. Workarounds and Gotchas

### Code Block Rendering Bug

Manim has a known bug where empty lines in Pygments cause an `IndexError` in `_gen_chars`. When rendering external code snippets using `Code()`:

1. Read the target lines from the source code.
2. Iterate through the lines and replace completely empty lines with a space and a newline (`" \n"`).
3. Replace tabs with 4 spaces to ensure consistent rendering.
4. Write the cleaned lines to a temporary file (e.g., `temp_cleaned_code.py`).
5. Pass the temporary file path to `Code(code_file=...)`.

### Highlighting Code Lines

To animate specific lines of code, access the underlying paragraph elements using `.code_lines` instead of indexing the `Code` object directly:

```python
code_window = Code(...)
code_lines = code_window.code_lines # Access the VGroup
self.play(code_lines[2].animate.set_color(YELLOW))

```

## 6. Mathematical and Visual Guidelines

* **Equations:** Use `MathTex` for equations.
* **Standard Text:** Use `Text`.
* **3D Scenes:** Remember to set the initial camera orientation (e.g., `self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)`).
* **Performance:** Use `use_smoothing=False` on highly granular plots to speed up rendering if necessary.

```

```
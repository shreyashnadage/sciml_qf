---
trigger: model_decision
description: use these rules while writing any scene that has code snippet to be rendered in it.
---

```markdown
# Manim Community: Code Object Rules & Standards

**Context:** This document outlines the standards, known bugs, and workarounds for using the `Code` mobject in Manim Community (v0.20.1+) within this repository. Manim's `Code` API is highly volatile, and direct usage of unstable arguments will cause pipeline failures.

**Agent Directive:** Any agent or developer writing Manim scenes involving the rendering of code snippets must strictly adhere to the patterns and rules below.

---

## 1. Known Issues & Solutions Encountered

| Issue / Error | Cause | Solution |
| :--- | :--- | :--- |
| `TypeError: unexpected keyword argument 'file_name'` | The parameter name changed in recent Manim versions. | **Do not use `file_name`**. Use `code_file` instead. |
| `TypeError: unexpected keyword argument 'font_size'` | The `Code` object does not accept size parameters directly in its constructor. | **Do not pass `font_size`**. Instantiate the object first, then call `.scale(0.65)` on it. |
| `TypeError: unexpected keyword argument 'code'` | Passing strings directly to the constructor via `code=` or `code_string=` is unstable across minor versions. | **Do not pass raw strings directly.** Write the string to a temporary file and use `code_file`. |
| `IndexError: list index out of range` (in `_gen_chars`) | Manim's Pygments parser crashes when it encounters completely empty lines (`\n`) or certain tab characters. | **Sanitize lines before rendering.** Replace empty lines with `" \n"` (space + newline) and replace tabs with 4 spaces. |
| `AttributeError: Code object has no attribute 'code'` | The attribute holding the rendered text `VGroup` was renamed from `.code` to `.code_lines`. | **Use `my_code_obj.code_lines`** to access the text for animations. |
| `[WARNING] SoX could not be found!` | Manim looks for SoX for audio processing, but our pipeline handles audio via FFMPEG. | **Ignore this warning.** It is non-blocking and does not affect the render. |

---

## 2. The "Bulletproof" Code Instantiation Pattern

To avoid all API volatility and Pygments parsing bugs, **you must use the following pattern** whenever rendering code on screen. Do not try to take shortcuts with string parameters.

```python
import os
from manim import *

# 1. Define paths
original_file_path = "path/to/source_code.py"
temp_file_path = "media/temp_cleaned_code.py" # Use a temp file for safety

# 2. Read the original source code
with open(original_file_path, "r") as f:
    lines = f.readlines()

# 3. Extract the needed lines (e.g., lines 47 to 68)
target_lines = lines[46:68]

# 4. SANITIZE: Fix the Manim empty-line Pygments crash bug
cleaned_lines = []
for line in target_lines:
    if line.strip() == "":
        cleaned_lines.append(" \n")  # CRITICAL: Must have a space before newline
    else:
        cleaned_lines.append(line.replace("\t", "    "))

# 5. Write sanitized lines to the temporary file
with open(temp_file_path, "w") as f:
    f.writelines(cleaned_lines)

# 6. Instantiate Code securely using `code_file`
rendered_code = Code(
    code_file=temp_file_path,
    language="python",
    background="window"
)

# 7. Scale and position AFTER instantiation
code_window = rendered_code.scale(0.65).to_edge(LEFT)

```

---

## 3. Animating Code Lines

When you need to animate or highlight specific lines of code during a scene, you must access the internal `Paragraph` object (which is a `VGroup` of the lines).

* **Incorrect:** `rendered_code.code[2].animate.set_color(YELLOW)` ❌
* **Correct:** `rendered_code.code_lines[2].animate.set_color(YELLOW)` ✅

### Example of Synchronized Highlighting:

```python
# Access the VGroup of rendered lines
code_lines = rendered_code.code_lines

# Animate highlighting line index 2 (the 3rd line of the snippet)
self.play(
    code_lines[2].animate.set_color(YELLOW), 
    run_time=1.0
)

# Un-highlight line 2, and highlight line 3
self.play(
    code_lines[2].animate.set_color(WHITE), 
    code_lines[3].animate.set_color(YELLOW), 
    run_time=1.0
)

```

```

```
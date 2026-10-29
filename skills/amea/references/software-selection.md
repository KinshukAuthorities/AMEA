# Medium and software preferences

Use [canonical workflow selection](workflow-selection.md) before creating production assets. Reuse explicit user choices and an existing project's medium/software. For a new unspecified anime request, the documented default is authored drawn 2D in Blender Grease Pencil: state and record it, then proceed without asking the user to choose again. A specific user preference overrides the default and an inference from attached media; supplying a video does not decide the workflow by itself.

Ask only for a genuine unresolved choice not covered by the default or inherited contract, such as software for explicitly requested 3D or incompatible requirements. If the user delegates such a choice, select a suitable available tool and record it. While an essential answer is pending, inspect supplied material and continue independent planning; do not replace the requested method with an unrelated available backend.

Save `preferences.medium`, `preferences.software`, and relevant version/tool paths in the project. Verify actual native file support, scripting or UI control, drawing or rigging capabilities, rendering, audio support, and export. Tool installation is not proof that the current AI host can operate it. Use the host's supported interface and respect the chosen production method.

Blender Grease Pencil is the default drawn-2D implementation; the contour helper is an optional transport optimization within that method. Krita execution and the Krita-only helper apply when Krita is explicitly selected or inherited. Other requested software uses its supported native tools. Preserve the canonical construction/review discipline and useful editability; do not fabricate a native document or silently switch applications.

Reuse installed dependencies first. Install missing libraries into an isolated project environment when needed for the selected workflow. Do not install a whole editor, tensor framework, model checkpoint, or unrelated backend for a task that does not need it. Missing access, platform incompatibility, or a required paid service needs a precise explanation and an appropriate alternative or user decision.

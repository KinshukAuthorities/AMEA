# Dependencies and local execution

AMEA contains authored skills, references and helpers. It does not ship Python, libraries, editors, downloaded generator source or model weights. `requirements.txt` is the single dependency file: its installable baseline supports image helpers, and comments identify optional backend dependencies and official setup links. Install only what the chosen workflow needs.

Establish missing medium/software preferences before production and reuse earlier choices. Discover the selected editor and its supported controls. Run `python tools/dependency_doctor.py` with available Python to inspect helper dependencies and optional tools; this report does not prove GUI access or animation capability.

## Generation access and user choice

Prefer suitable hosted TRELLIS.2 for new 3D assets; read [asset generation](asset-generation.md) before setup. Use supplied images or create missing references with available tools. A hosted GLB export needs no local inference framework or checkpoint.

If the required model or usable generation route is unavailable, or online access is blocked, explain the concrete blocker and ask the user which available route to take. Offer prepared-image/asset handoff, suitable local generation, or another method as relevant. Wait for that decision before switching methods, downloading a local model or installing its inference stack. Reuse a choice already made; do not ask again or infer a fallback from an installed package. Continue independent planning while waiting.

## Selected local setup

After local generation has been selected, inspect this user's OS, GPU architecture/VRAM, RAM, storage and available time. Reuse compatible installed environments and verified caches without modifying another project's environment. Check the chosen model's current official setup, checkpoint and platform support. Do not assume every user shares a previous machine's limits.

Create an isolated project environment when needed and install only missing dependencies for that selected model. Keep compatible framework, CUDA and extension versions together. Test real imports and a small generation, preserving source revision, checkpoint identity, settings and provenance. Package presence or a tensor smoke test alone does not prove the generator works. Preserve licenses and relevant notices. Diagnose unfamiliar upstream failures before applying source changes.

Applications and host capabilities are separate from pip dependencies. Use the selected editor and compatible FFmpeg/FFprobe binaries when needed. Do not install a new editor, GPU driver, CUDA toolkit, server or unrelated backend by habit. Image generation, speech tools and service access require actual available capabilities.

Before scaling, demonstrate the production route appropriate to the requested stage as described in [first-delivery acceptance](first-delivery.md). A static mesh or dependency report does not establish consistent animation, expressive controls, usable sound or editable delivery.

## Helper boundaries

`amea_project.py` manages the optional Krita drawing evidence/timing contract; it does not draw or control the UI. Blender rendering and audit helpers run through the selected Blender executable. For another editor use its supported native tools and equivalent evidence. Helpers do not certify artistic quality, source fidelity, contact or subjective audio review.

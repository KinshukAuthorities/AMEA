# Dependencies and local execution

AMEA contains authored skills, references, and helpers. It does not ship Python, PyTorch, common libraries, editors, downloaded generator source, or model weights. `requirements.txt` is the dependency catalog with workflow profiles and external tool/model links. Install only the profile and tools the chosen workflow needs.

Prefer suitable hosted TRELLIS.2 for new 3D assets; read [asset generation](asset-generation.md) before any local installation. Use supplied reference images or create missing ones. A successful hosted GLB export requires no local PyTorch or generation checkpoint. For blocked hosted access, offer prepared-image/GLB handoff or an appropriate local backend and reuse the user's decision.

Before production, establish medium and software preferences. Run `python tools/dependency_doctor.py` with an available Python, discover the chosen editor and its supported API, and inventory existing environments and model caches. Reuse a working installation before installing another one. Do not modify another project's environment to satisfy this one.

Create a project-local environment only when needed. Install the selected workflow's missing dependencies; installing the complete optional 3D stack for simple 2D editing wastes time and disk. Keep the compatible PyTorch/torchvision pair and choose CPU or CUDA wheels for the actual machine using PyTorch's official selector. Test a real tensor operation and generator import, not merely package presence. Do not install a CUDA toolkit or new GPU driver by habit.

Applications are separate from pip dependencies. The user chooses the editor. Discover or install only that editor when needed; Blender and Krita are supported optional paths. FFmpeg and FFprobe handle media assembly and checks. Choose compatible binaries for the OS and keep their original notices. API access, paid generation, voice synthesis, and host image generation are not supplied by Python package installation.

Before scaling, demonstrate the actual selected production route as described in [first-delivery acceptance](first-delivery.md). A dependency report, tensor smoke test or generated static mesh is not proof of consistent animation, expressive controls, usable sound or editable delivery. Test those required capabilities through real artifacts.

## Optional local TRELLIS.2

Use the official source, checkpoint, and installation procedure linked in `requirements.txt`. Inspect the current hardware/software requirements and compatible extension stack before setup. A capable user's machine can run a suitable local configuration; do not assume all users share a particular GPU or operating system. Record the source revision, checkpoint identity, environment, output settings, and a real generation smoke test.

Use a separate environment for backend-specific PyTorch/CUDA extensions. Do not force the Hunyuan version pins onto TRELLIS.2. Download only required weights and dependencies when local generation has been selected. Community builds require their own compatibility verification.

## Optional local Hunyuan fallback

When this fallback suits the task, use its official source and checkpoint listed in `requirements.txt` and the `requirements-hunyuan.txt` profile. Reuse local source/weights if present. Record revisions, hashes, licenses and local changes. The known FP16 shape weight file is 3,819,958,234 bytes with SHA256 `3cc66f3bea33e4062b7dbc875ffe1d70c4888914aec3e91b60f94e9bd01b522b`; verify an exact copy against that identity. A different checkpoint needs its own identity and compatibility test.

Keep the model's `config.yaml` alongside its weights. Preserve upstream `LICENSE` and `NOTICE`. Use `tools/hunyuan_compat.py` to check/apply the known compatible decoder fix only against the expected source structure; unfamiliar versions require inspection. Retain modification notices and original source backups.

Use `tools/generate_mesh.py` with explicit source, checkpoint, image, and output paths. This runner loads local files and does not automatically download a model or start a server. It uses chunked hierarchical surface extraction, the execution-device/offload compatibility setup, and optional isolated-component cleanup. Inputs need actual image references. Outputs are unrigged meshes, not completed animation or textured, expression-ready characters.

Set CPU threads and query chunks according to measured memory and throughput. Keep large GPU inference sequential on constrained hardware. CPU inference may be possible but slow; say so based on measurement. Do not silently substitute an unrelated service or backend when a capability is missing.

## Helper boundaries

`amea_project.py` manages Krita drawing evidence and timing; it does not draw or control the UI. The Blender renderer and audit run through Blender's Python, not ordinary pip `bpy`. For another editor, use its supported native implementation and preserve equivalent evidence. Helpers do not certify artistic quality, source fidelity, collisions, or subjective audio review.

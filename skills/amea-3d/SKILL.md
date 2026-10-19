---
name: amea-3d
description: Build and animate original or source-guided 3D anime scenes in the user's selected software, with modeling, materials, rigs, skinning, expressive performance, camera staging, local mesh generation, rendering, and deformation review.
---

# AMEA 3D Production

Honor the requested subject and result; characters and organic rigs are optional. Read [asset generation](../amea/references/asset-generation.md), [3D asset production](../amea/references/3d-production.md), [motion and interaction](../amea/references/motion-and-contact.md), [performance](../amea/references/performance.md), [review](../amea/references/review.md), and [3D project format](../amea/references/3d-format.md). Read [runtime](../amea/references/runtime.md) for local setup and [audio](../amea/references/audio.md) for timing.

Reuse the user's established software choice. If absent, ask before production along with any missing 2D/3D preference. Native scene and scripting operations depend on that choice. Blender-specific helpers are optional and do not authorize switching applications.

Read [brief to performance](../amea/references/brief-to-performance.md) and [parallel production workers](../amea/references/parallel-production.md). Overlap asset/reference creation with story/action/camera planning and independent setup or sound work. Plan on labeled proxies, then fit final poses, reach, contact and framing to accepted real geometry and rigs. Use separate file ownership and one desktop-input queue.

Prioritize [computer-vision review and repair](../amea/references/visual-review-and-repair.md) over script-only acceptance. Inspect actual mesh deformation through consecutive frames, including limb orientation, support and contacts. Correct visible failures and visually retest before marking them resolved, even when bone lengths and transforms pass numerical checks.

## Establish the design before animation

Choose and record the style, proportions, coordinate basis, scale, materials, construction, and required views. Compare actual neutral renders and representative expressions against stable references. More surface detail cannot repair incorrect structure or silhouette. For original assets, author geometry and rigs; use existing or supplied assets only when consistent with the brief and permissions. Generation model weights are tools, not ready-made scene assets.

Use supplied asset images or create missing references with an available image/drawing tool. Prefer TRELLIS.2 as the first image-to-3D candidate, trying its official hosted workflow before a local install unless the user's constraints favor local processing. Export and inspect the actual GLB. On a concrete access blocker, offer user generation from the prepared images and GLB handoff or a hardware-appropriate local setup. Reuse an established choice. Select another suitable method when context warrants it; do not lock the project to one model.

The Hunyuan mesh runner is an optional local fallback and requires its own source, weights, and dependencies. Neither it nor a hosted GLB guarantees good topology, likeness, a rig, or correct deformation. Inspect those before animation, and adapt setup to the current user's hardware rather than a previous computer's limits.

## Build a performance-ready scene

Use joints and controls fitted to the actual form. Separate object movement, rig motion, deformation, facial controls, materials, and cameras. Preserve rest transforms, apply coordinate conversions deliberately, and use scale-consistent constraints. Test representative extremes before baking a long performance. Fix wrong region weights, collapsed joints, twisted axes, penetration, and drifting attachments at their source.

Author meaningful poses and timing, including preparation, action, contact or change, reaction, recovery, and settling where appropriate. Define paths, spacing, silhouettes, balance, gaze, expressions, overlapping motion, and dependent reactions. Avoid repetitive neutral poses or uniform interpolation when the brief calls for expressive performance. Use facial and hand posing appropriate to the subject; speech-driven mouths require actual speech timing.

Plan camera geography with the action. Keep important forms readable, preserve intended screen direction, and check framing through the entire shot. Effects and camera shake support performance; they do not replace it. Review quiet and transitional intervals as well as action peaks.

## Review cheaply, then render

Save reusable asset and scene caches. Use viewport proxies or reviewed render LODs while retaining full editable assets. Render a representative short sequence, watch it at the intended speed, and inspect critical poses. Check that the moving blockout delivers the brief's performance and camera intent; correct weak staging or repetitive motion as well as mechanics and deformation before committing to a long high-quality render.

Use the selected application's native API for audits and resumable rendering. The package's Blender helpers are available when Blender is selected. Helpers do not choreograph, model, judge quality, or certify collisions. Review real mesh surfaces and the actual encoded output. Bound worker count using measured CPU, RAM, GPU and VRAM behavior; more processes can slow the job down.

Deliver the selected application's native scene, packed or correctly linked required assets, useful source scripts, timing and audio, the requested export, and truthful review evidence. A 3D project does not require a fabricated drawing document or a drawn-animation validation claim.

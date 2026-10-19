# Asset references, online generation, and local fallback

## Use the right inputs

Use relevant asset images supplied by the user as the design authority. Inspect them before changing or regenerating anything. Reuse accepted references already in the project. If images are missing, create a consistent reference set with an actually available image-generation or drawing tool, using the brief and any supplied visual constraints. Do not make the user supply images the agent can create itself. If that capability is unavailable, explain the specific gap and request the needed input.

Prepare clean, reusable asset images and preserve their identity, prompts where available, intended views, scale/proportions, palette, and alpha. Keep views consistent rather than independently inventing each one. Provide genuine transparency when isolation is intended, and inspect both pixels and alpha. Do not fabricate unseen geometry as an observed fact. The needed views and pose depend on the subject and generator; do not force a character sheet onto every asset.

## Preferred starting point for 3D

Prefer **TRELLIS.2** as the first candidate for image-to-3D assets, especially when a hosted run can provide geometry and PBR materials without a local installation. This is the user's preferred starting point, not a claim that one model wins every task. Let actual reference fidelity, topology/material needs, access, reliability, time, and resource constraints guide the final choice. Test the produced asset rather than judging it only by model reputation.

Official discovery links that the agent must know:

- [TRELLIS.2 official online demo](https://huggingface.co/spaces/microsoft/TRELLIS.2).
- [TRELLIS.2 project and capabilities](https://microsoft.github.io/TRELLIS.2/).
- [TRELLIS.2 official source and local requirements](https://github.com/microsoft/TRELLIS.2).
- [TRELLIS.2 official weights](https://huggingface.co/microsoft/TRELLIS.2-4B).
- [Hunyuan3D official source and alternatives](https://github.com/Tencent-Hunyuan/Hunyuan3D-2).

Verify that the service is actually reachable and supports the needed export. Use a supported browser or documented API. The official TRELLIS.2 demo provides generation followed by an **Extract GLB** export; creating a preview alone does not save the mesh. Inspect views, extract the asset, and download its GLB with required textures/materials before calling generation complete. Do not assume every similarly named website is Microsoft's official service, or that the host is always available or unrestricted.

## Choose execution without unnecessary setup

Try suitable hosted generation first unless the user has requested local/offline processing or relevant constraints favor another method. Local GPU limitations do not constrain the remote GPU. Do not reject online TRELLIS.2 because the user's PC has little VRAM, and do not install PyTorch or download multi-gigabyte weights merely to use a hosted generator.

If the online workflow succeeds, continue with the downloaded assets in the selected animation software. If a temporary error is plausibly transient, use a bounded retry. Avoid repeated blocked submissions or switching to paid services silently.

If login, quota, payment, access, missing browser/API capability, or another concrete blocker prevents hosted generation, explain the actual blocker and offer the relevant practical choices in one concise question:

- The user runs the prepared reference images through the linked generator and supplies the resulting GLB and any companion assets. Save a ready-to-use reference folder, generation settings/request, and export directions so the user does not have to recreate the setup.
- The agent sets up local generation, reusing installed tools and verified cached weights or downloading only missing requirements.
- Another available suitable service or native modeling method, when the situation supports it and the user accepts that route.

Reuse a choice the user has already made. Do not ask for secrets, bypass access limits, or treat elapsed time as permission for payment. Do not demand a local download when the user can return generated files. While external generation is pending, continue independent planning and preserve the exact pending asset handoff.

## Evaluate local resources for this user

Inspect the current user's OS, GPU architecture/VRAM, RAM, storage, installed dependencies, and available time. Do not encode one previous machine's limitations as a universal rule. A capable machine may support local TRELLIS.2 well; a constrained machine may favor hosted processing or a lighter backend.

Check the selected backend's current official setup and dependency versions. TRELLIS.2's official documented reference setup uses Linux and a large NVIDIA GPU; community ports/offloading may differ and need their own smoke test. The Hunyuan helper is a separate optional fallback, not a reason to replace the preferred model on every system. Do not mix incompatible CUDA-extension stacks in one environment.

Choose a backend intelligently rather than cycling through every model. When the preferred method is suitable and accessible, proceed. A different model or manual construction may fit a particular asset, software, hardware, or edit better. The presence of a Hunyuan-specific helper does not override the TRELLIS.2 preference or require offline generation. Record the reason for a material change of method and preserve user-specified constraints.

For a user-operated handoff, `tools/asset_handoff.py` can copy the selected reference images and brief into a new folder, record hashes, write export directions, and create a small handoff ZIP. It does not upload images, generate geometry, or imply the returned asset has been reviewed. Use the primary conditioning image accepted by the service; supplementary views remain design/review references unless the selected service supports them as inputs.

## Integrate and verify the actual asset

Inspect downloaded or user-returned files: geometry, silhouette, hidden surfaces, orientation, scale, materials, opacity, UVs, texture files, attachments, topology, and deformation suitability. Preserve source identity and generation provenance. A new asset generated online from the project's references is distinct from downloading an existing ready-made asset; respect whichever provenance constraints the user gave.

Import into the chosen software, correct or retopologize as needed, create the required rig/controls, skin and test deformations, and then animate. GLB is an interchange container, not proof that a skeleton, facial rig, correct weights, or usable motion is present. A good static model does not solve acting, contacts, cameras, expressions, continuity, or timing automatically.

For existing usable native assets, simple edits, or tasks that do not require a new 3D model, skip asset generation entirely. The purpose of this workflow is the user's animation, not demonstrating a particular generator.

# Efficient production and resuming

Inspect installed capabilities once, then reuse verified tools and accepted assets. Use native APIs for repeatable operations and supported interfaces for visual judgment. Avoid repeated file dialogs, reinstalls, checkpoint downloads, or full scene rebuilds for local corrections.

Use inexpensive but representative tests before finishing. Judge design, articulation, interaction, and framing with consecutive frames and actual playback. Reduced resolution is useful only if it preserves the evidence needed to assess the defect. Correct rough mechanics before spending time on detailed textures, lighting, or full-length rendering.

Separate design, geometry, rigs, performance, scene assembly, sound, and delivery caches. Changing movement should not regenerate a sculpt; changing one contact should not rebuild every background. Preserve full native assets while using reviewed proxies or LODs. Record completed artifacts, their input identities, unresolved corrections, and the next action so another agent can resume.

## Production workers and bounded compute

Use [parallel production workers](parallel-production.md) for overlapping assets, story/action/camera planning, setup, contextual sound planning and visual review. Start ready planning tasks while generation runs, and review completed intervals while later independent work continues. Follow the shared revision, dependency and single-writer contract.

Agent workers and CPU processes solve different scheduling problems. Also parallelize independent frame rendering, reference preparation, inspection, hashing or packaging when useful. Keep dependent final decisions, shared native-document edits and memory-limited GPU inference ordered. Multiple agent workers never authorize simultaneous GUI input or competing writes to one document.

Benchmark a representative range with one worker, then a bounded additional worker when resources permit. Measure aggregate throughput, startup/shader cost, CPU saturation, RAM, GPU/VRAM, disk behavior, and failures. More processes can slow production through oversubscription, swapping, duplicate compilation, or GPU contention. Divide thread budgets between processes and leave resources for the desktop.

Choose samples, resolution, motion blur, effects, and LOD deliberately and review changes. Never replace changing poses with still-image transforms merely to export faster. Report actual completed frames and measured progress; do not invent an ETA.

## Cache integrity and correction ownership

Include the native scene, required external assets, relevant scripts, settings, and tool version in render identity. An existing PNG or old completion flag does not establish that a frame matches current inputs. Separate output generations by identity and preserve earlier revisions.

Pack native assets or declare all external dependencies. The optional Blender queue hashes declared inputs, assigns disjoint ranges, writes PNG frames atomically, and resumes validated frames from the same generation. Undeclared external changes can still invalidate a cache; the agent must maintain that contract.

Correct native source first and invalidate all causally affected work. Render a local replacement only after earlier writers for that range have stopped. Record replaced intervals and their inputs. Never run competing writers for the same frames or encode while corrections are pending. Validate the entire sequence before encoding, then decode and review the actual final output.

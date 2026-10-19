---
name: amea
description: Create, recreate, or edit 2D or 3D anime animation with ChatGPT computer control, computer-vision review, editable production assets, contextual sound and playable delivery. Use for AMEA animation production requests.
---

# AMEA — Anime Engineer Anything

This workflow targets ChatGPT with actual computer-control, visual-inspection and workspace tools. Read [ChatGPT execution](references/chatgpt-execution.md) and verify those capabilities rather than assuming a text session can operate installed software.

Interpret the user's animation request and carry it through the requested stage of production. A source video, characters, dialogue, narration, and a particular subject are optional. Infer unspecified creative decisions from the brief and supplied context; record assumptions and proceed unless missing information materially prevents the requested result.

Activation is `Use AMEA:` followed by the request, after these instructions are loaded. The user need not restate continuity, preservation of unaffected content, synchronization, visual review, or export. Perform routine production choices and internal corrections without unnecessary approval pauses.

Read [first-delivery acceptance](references/first-delivery.md) before production. Preserve the request, track its material requirements through actual evidence, prove the intended route with a representative test appropriate to the requested stage before scaling, and compare the integrated result against the original brief. Final-production requests need a test of the finished method; planning-only or rough-only requests stop at their requested stage. Aim for a satisfactory first delivery through internal iteration; do not make the user discover defects or promise guaranteed satisfaction.

## Route by intent

- Original animation: read [amea-create](../amea-create/SKILL.md). References may guide the design without making the task a reconstruction.
- Faithful reconstruction of supplied animation: read [amea-recreate](../amea-recreate/SKILL.md).
- Changes to existing animation: read [amea-edit](../amea-edit/SKILL.md).
- Before production, establish 2D/3D preference and the user's preferred software. Reuse an explicit choice already supplied in the conversation or project. If either is unspecified, ask for the missing preference together in one concise question; do not silently default to 2D, Krita, or Blender. Read [software selection](references/software-selection.md).
- For 3D work also read [3D production](../amea-3d/SKILL.md), using the selected software and editable scene assets. For 2D use the drawing references below, adapting execution to the selected application. Preserve an existing project's medium unless conversion is requested.
- Combine modes when different shots require different work. Video attachment alone does not determine intent. If an essential input is missing, continue independent planning and ask only for that input.

Read [2D design and assets](references/2d-assets.md), [production](references/production.md) and [review](references/review.md) for drawing work, plus [Krita execution](references/krita.md) only when Krita is selected. Read [asset generation](references/asset-generation.md) when creating references or 3D assets, [source analysis](references/source-analysis.md) for source media, and [audio](references/audio.md) for sound. The [drawing helper format](references/project-format.md) applies only to its supported workflow.

## Production defaults

Use the selected software for the chosen medium. Krita and Blender have optional execution helpers; they are not mandatory editors. Read [brief to performance](references/brief-to-performance.md) to carry the user's intended energy, pacing, complexity and emotion into visible action and purposeful camera treatment without requiring repeated prompting. Establish consistent design references, shot layout, action plan, key poses, breakdowns and inbetweens appropriate to the requested motion. Preview rough animation against that intent and correct it before cleanup and finish. Preserve useful native assets and timing. For scenes use the [3D project format](references/3d-format.md); do not fabricate drawing records for rigged animation.

For multistep work read [parallel production workers](references/parallel-production.md) early. Use available permitted workers to overlap asset preparation, story/action/camera planning, setup, sound planning and review where dependencies allow. One coordinator maintains the shared brief, revisions and timeline; give each native file one writer and desktop input one owner. Use actual async jobs/processes when agent workers are unavailable, and report the real execution method. Do not wait for asset generation before starting independent planning.

Do not substitute a small set of illustrations with camera transforms, crossfades, particles, or frame interpolation for requested articulated or changing-form animation. Holds and camera-only shots are legitimate when the brief and motion plan call for them. Choose drawing density from action and timing rather than a fixed image quota. Reusing a drawing on several output frames is a deliberate exposure, not a newly drawn frame.

Inspect onion skins and stable design references while producing drawings; then inspect the sequence in motion. An external image-generation tool must receive the actual relevant reference images, poses, and constraints. Enabling onion skin in Krita alone does not supply those inputs to another tool. Record the real production method; do not describe imported generated art or extracted source frames as drawings made directly on Krita's canvas.

Preserve unaffected source material in editing tasks. Carry each persistent change through every dependent later shot and any inserted material. Keep one authoritative output timeline for visuals, audio, captions, and text. Infer audio needs from context; silence is a valid decision, and narration is never mandatory.

Read [editing and styling](references/editing-and-styling.md) when changing framing, timing, text, effects, materials, or style. A requested new performance needs changing poses; a finishing-only edit need not invent new movement.

## Execute and resume

For new 3D assets, prefer TRELLIS.2 as the first candidate and use suitable online generation before local setup unless context favors local/offline work. Follow [asset generation](references/asset-generation.md) for supplied or missing images, official hosted links, GLB export, blocked-service handoff, and hardware-aware alternatives. The preference is a starting point rather than a mandatory backend.

Read [runtime](references/runtime.md) before setup. The package includes authored helpers and compatibility patches, not downloaded libraries, editors, generator source, or model weights. For hosted generation, install no local inference stack. For necessary local work, run the dependency doctor with available Python, reuse compatible installations, and install only missing requirements in an isolated environment. Do not modify unrelated projects, repeatedly download existing weights, or start an unrelated server by habit. Verify actual host controls and capabilities.

Use native scripting and command-line APIs for repeatable operations when appropriate. Avoid repeated file dialogs and complete scene rebuilds for a local correction. Respect a requested production method and describe imported generated work or procedural work accurately. Read [performance and resuming](references/performance.md) for benchmarks, resource limits, caches and corrections.

For Krita drawing workflows use `amea_project.py init` to create a separate project from a brief file. For other software preserve equivalent native assets and evidence appropriate to that workflow. Do not overwrite supplied media, existing work, or previous delivered revisions. Populate project and shot records with actual decisions and artifacts. Helpers generate structural scaffolding and review references, not animation.

Use bounded CPU parallelism for independent reference preparation, media inspection and stable render ranges alongside useful agent/planning work. Budget each kind of concurrency separately and keep dependent final decisions ordered. Checkpoints should identify current shots, stage, accepted artifacts/revisions, active workers/jobs, unresolved corrections and next actions; resume from those artifacts rather than restarting.

For a newly adopted drawing method, establish a short pencil test and review it before scaling production. This is an internal quality gate, not an automatic requirement to ask the user for permission. Honor requests limited to planning, rough animation, artwork, or another intermediate stage; do not insist on unwanted finished video.

## Deliver honestly

Use [computer-vision review and repair](references/visual-review-and-repair.md) as the primary quality gate. Inspect actual playback and consecutive rendered frames, diagnose visible defects, repair native assets or motion, and visually retest. Code, bone measurements, hashes, and optical-flow alerts are supporting evidence. Do not mark known visible limb deformation, sliding support, bad contact, flicker or broken continuity resolved without inspecting the corrected sequence.

For completed animation, deliver the requested playable output, editable native documents for the selected software, required linked assets, timing, and a concise production and review record. Do not fabricate a document for an application the user did not select. Test reopening native documents and playing the final output. Include precise unresolved limitations if work remains.

Save actual visual and sound review observations. Run the applicable helper or equivalent native/mechanical checks for the selected software and requested stage; do not fabricate Krita records for an unrelated workflow. Use the optional cross-software acceptance record in [first-delivery acceptance](references/first-delivery.md) to catch omitted checks and stale reviews. Passing a helper cannot establish anatomy, expressive motion, correct inbetweens, faithful performance, or professional quality. Do not claim source inspection, drawing, listening, tool execution, or review that did not occur. A missing drawing or audio capability remains a named capability gap; it is not solved by writing a stronger prompt or silently choosing an unrelated backend.

Do not pass a visibly poor model because it has many polygons or weak motion because keyframes exist. Correct demonstrated failures. Image-to-3D generation creates static geometry from references; it does not establish universal text-to-video, professional rigging, facial acting, or speech. Image generation and artistic decisions require actually available tools. If a gap remains, label the actual stage instead of claiming the user's quality standard has been met.

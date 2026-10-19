# Native 3D project and render contract

Store a brief, established medium/software preferences, design references, source identities, native scene/assets, shot/action plan, authoritative timing, audio decisions, dependency identities, checkpoint status, and real review observations in the project. Use project-relative paths where practical. Keep source media and earlier revisions intact. A 3D project must not claim drawing evidence or a Krita validator pass.

The native scene must preserve useful object structure, geometry, materials, rigs, animation, expressions where applicable, cameras, lighting, and required external assets. Record inferred versus observed geometry for reconstruction. Keep generation inputs, seeds, settings and hashes when used. A rendered video alone cannot recover editable geometry or performance controls.

## Optional Blender render job

`python tools/render_queue.py <job.json> --blender <executable> [--workers <count>] [--threads <count>]` renders an already-authored Blender scene. It does not create assets or movement. All declared paths are relative to the job file unless absolute input paths are deliberately supplied. `output_dir` must stay inside the job's folder tree.

The job is a JSON object with these fields:

| Field | Meaning |
| --- | --- |
| `scene` | Saved native Blender file. |
| `start`, `end` | Inclusive integer output frame range. |
| `fps` | Positive rational output frame rate. |
| `width`, `height` | Positive even output dimensions. |
| `dependencies` | Required external input files whose content affects the render. Pack assets or declare them here. |
| `output_dir` | Project-local render root; each input identity gets its own generation folder. |
| `samples` | Optional positive Eevee sample count. Other render settings remain native. |
| `audio_mix` | Optional prepared, output-aligned audio file. No dialogue is invented by this renderer. |
| `encode` | Boolean selecting H.264 delivery after sequence validation. Defaults to true. |
| `review_frames` | Optional output frame numbers to extract from the encoded result for visual review. |

The queue hashes declared inputs, helper source and effective settings. Each worker owns a disjoint range, validates cached images, and writes replacements atomically. Changes create a new generation; old frames are not mixed in silently. Reports identify actual dimensions, duration, frame rate, decoded frame count and audio presence. Artistic and listening review remain pending until the agent performs them.

## Optional rig/contact audit

Run `blender -b <native-scene> --python tools/blender_audit.py -- --output <report.json> [--frames <frame numbers>] [--contacts <contacts.json>]`. The tool records sampled posed bone/rest length ratios and target distances. It does not certify nonintersection, joint health, likeness, or correct performance.

The optional contacts file is a list of records. Each record has `frame`, `object`, optional `bone`, `point` equal to `head` or `tail` for a bone, and either a `target_object` or a three-number world-space `target`. An object target uses its origin, so use an explicitly placed contact marker when that represents the intended surface. Add a scale-appropriate `tolerance` when a numerical threshold is useful. Actual surface contact and swept geometry still require review.

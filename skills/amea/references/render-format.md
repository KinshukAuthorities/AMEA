# Drawn animation render jobs

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

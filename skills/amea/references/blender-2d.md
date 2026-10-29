# Drawn 2D animation in Blender

Read this when Blender is selected for 2D work. Use [drawn anime construction](drawn-anime.md) for the artistic decisions, [motion and contact](motion-and-contact.md) for mechanics, and [first-delivery acceptance](first-delivery.md) for the requested deliverable. This route creates editable Grease Pencil drawings. A moving 3D camera does not turn a flat cutout into a constructed new view.

## Choose the authoring method deliberately

Use native drawing tools, authored contours, or another available drawing method consistent with the user's constraints. A native contour helper transfers the supplied art; it does not design characters or invent good poses. Programmatic contour entry is not physical stylus drawing. Do not use raster tracing, generated images or generated video where the requested method excludes them. Do not replace detailed illustrative construction with the helper's calibration geometry.

For a new design establish the relevant views, proportions, silhouettes, facial construction, palette and line treatment. Test the most demanding view or deformation before expanding drawings. Keep the complete figure under one accountable pose owner during a coupled action; independent backgrounds, effects and review can proceed in parallel. Workers may prepare separate contributions, but one integrator writes each native document. Read [parallel production](parallel-production.md).

Use the actual rendered camera for framing and cloth/limb occlusion tests. A large isolated design sheet can conceal errors that appear at delivery size. For an orbit, establish a projection contract: world/local pose and root travel, constructed relative view, drawing projection, camera framing, then compositing. Apply projection and root transforms once. A drawing already projected into scene XY normally needs an identity actor transform. Keep world-ground contact landmarks separate from lifted foot landmarks.

## Calibrate the native path before scaling

`tools/blender_2d.py` is an optional, dependency-free native transport helper. Run it using Blender's bundled Python. Its calibrated backend is Blender 5.2.2. The selected application may use another version or another native method; do not install or switch software merely to use this helper. On another version, use `--allow-unverified-version` only for an isolated calibration, inspect the results, and retain the report's unverified status until that backend is actually tested. A version flag never certifies compatibility.

Before a long production, exercise the actual intended line widths, curves, compound fills/holes, overlap order, translucency, changing poses, holds, camera and sound packing as applicable. Save and reopen a small native file in a fresh process and render representative frames. Inspect native editability and real pixels. Test the hardest finished-method interval using production art before rendering the rest; a synthetic transport test proves only transport.

The helper writes each pose as an ordered set of separate fill and ink curves in one native drawing per layer. It transfers point/curve attributes in bulk instead of making a native layer for every line. Each path's fill precedes its ink, followed by the next authored path. Compound subpaths retain their shared fill identity. This avoids both excessive native operations and a global “all fills, then all ink” reorder that can break occlusion. `AMEA_CURVE_INDEX.json` embedded in the native file maps curves back to source path IDs. Full native pose drawings remain editable; this is not a bitmap plane or rigged mesh.

For any alternative transport optimization, compare representative renders with an unoptimized reference using the same authored paths. Include overlaps, transparency, the difficult view and support extremes. Exact pixel equality is useful for a change intended to preserve pixels; a deliberate visual change instead requires new visual review. Preserve the source precision and painter order. Avoid huge single-line metadata blocks when writing Blender Text data; embed formatted JSON.

## Authored scene contract

This format is separate from the [Krita drawing helper](project-format.md). Save a UTF-8 JSON file inside a production project, outside the AMEA package. It contains:

| Field | Meaning |
| --- | --- |
| `schema_version` | `1`. |
| `canvas` | Integer `width`, `height`, rational `fps` such as `"24"` or `"24000/1001"`. Prefer even dimensions for H.264 export. |
| `frames` | Positive output-frame count. Output intervals are zero-based and end-exclusive. |
| `camera` | One fixed sample at frame zero, or one explicit sample per output frame: `frame`, `centre: [x,y]`, positive `width`. This orthographic camera composes already constructed views. |
| `layers` | Ordered records with unique portable `id`, distinct `z`, `drawings` and `exposures`. Larger Z is closer to the camera. |
| `background` | Optional opaque `#RRGGBB` world colour; `null` requests transparent output. Partially transparent world colour is rejected. |
| `audio` | Optional existing project-relative mixed sound file aligned to the full output; starts at native frame 1 and is packed. The audio reader is validated before scene creation; listening remains separate. |

Each layer's `drawings` maps drawing IDs to path lists. A path has unique `id` within that drawing, `d` containing absolute SVG `M`, `L`, `C`, `Q`, `Z` commands, optional `order`, `stroke`, `fill`, `width`, `opacity` and `tolerance`. Coordinates use centred XY, positive X right and Y up. This is an authored geometric path format, not an SVG-file importer. Relative commands, arcs, SVG transforms and arbitrary extra fields are rejected. Flatten those operations deliberately before transfer.

Colours are `#RRGGBB`, `#RRGGBBAA` or `null`; omitted ink is black and omitted fill is absent. Filled subpaths must close explicitly and retain at least three sampled points. Ink width is a nonnegative scalar or `[start,middle,end]` full-width profile. Opacity is in `[0,1]` and multiplies both ink and fill material alpha. Do not rely only on point opacity to make a filled contact shadow translucent. Sampling tolerance defaults to 0.25 drawing units; choose it relative to the closest camera's scale and verify visible curves.

Layer `exposures` are ordered `{start,end,drawing}` records covering exactly `[0,frames)` without gaps or overlap. `drawing` names a drawing ID or is `null` for an explicit blank. Native frame is output frame plus one. The compiler inserts an additional blank key at native `frames+1` to terminate the hold. Consecutive identical drawings can share an exposure; nonconsecutive reuse does not imply a newly authored pose. Record approved-key identity in project evidence and verify exact reuse when expanding breakdowns.

A minimal **transport calibration**, not a character design:

```json
{
  "schema_version": 1,
  "canvas": {"width": 640, "height": 360, "fps": "24"},
  "frames": 2,
  "camera": [{"frame": 0, "centre": [0, 0], "width": 640}],
  "background": null,
  "layers": [{
    "id": "calibration", "z": 0,
    "drawings": {"sample": [{
      "id": "contour", "d": "M -40 -30 Q 0 50 40 -30 Z",
      "stroke": "#243342", "fill": "#8fb7ca80", "width": [1, 3, 1]
    }]},
    "exposures": [{"start": 0, "end": 2, "drawing": "sample"}]
  }]
}
```

## Compile, render and resume

Use the selected Blender executable; these commands assume it is on PATH:

```bash
blender --background --python-exit-code 1 --python tools/blender_2d.py -- project/scene.json --output project/film.blend
```

The compiler validates paths, timing, camera and audio before replacing its fresh working scene. It checks the selected backend's actual RNA hard limits, including resolution, rational frame-rate representation and the terminating blank frame, so unsupported settings fail instead of silently clamping. Run it in a dedicated background process, not against an unsaved user document. It refuses existing native outputs and writes a temporary native file before publishing the new one. Keep earlier revisions. The adjacent `.transport.json` records source/backend/native identities and actual native keys. It marks artistic and playback review pending; successful compilation is not an animation-quality pass.

Use the saved native for local and full renders rather than recompiling it for each range. `tools/render_queue.py` renders stable, already-authored Blender scenes with versioned caches and optional encoding. Its job `start` and `end` are **inclusive native frames**; for this helper's complete output use `start: 1`, `end: frames`. Declare external dependencies even when the native file is unchanged. Supply `audio_mix` for the encoded soundtrack; a packed sequencer sound is not automatically an FFmpeg input. Read [3D format](3d-format.md) only for the queue's software-independent render-job fields; do not fabricate rig or mesh records for drawn work.

Hold source/native inputs stable while workers render. Wait for the actual compile/save process to finish before dependent reopen or render jobs. A returned asynchronous job ID means it is still running. Match cached frames to native/source/backend/settings identities and their own content hashes; dimensions alone cannot identify a current frame. Reopen and compare sampled renders. After local repair, review its consecutive affected interval and boundaries before full expansion. Preserve unaffected approved assets; do not reset the gate's retry history by renaming the same failure.

## Delivery checks

Check the complete frame sequence, exact duration/rational FPS, one-frame indexing boundaries, native drawing exposures, curve editability and linked/packed assets. Inspect consecutive final-camera renders for body participation, face/ear/hair visibility, garment coverage, contact, secondary motion, parallax and fill edges. Use enlarged diagnostic strips where small overview cells hide the defect. Review the actual encoded output as well as native renders, including playback and listening when the tools support them. Full decoding and pixel comparisons are mechanical checks and cannot stand in for those observations.

Record which artifacts, ranges and revision hashes were actually inspected and the method used. A still-image pass must not be relabelled playback or sound audition. A reviewer from the same model family is not a cross-family or human review. Name remaining capability gaps precisely and deliver the actual requested stage without claiming professional quality from a passing helper. Return the playable output, editable native project, necessary assets and concise evidence; do not ship personal logs or private production materials in AMEA itself.

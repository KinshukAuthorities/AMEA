# Project and helper contract

This is the optional Krita drawing helper's format. For another selected application, preserve equivalent native assets and evidence without claiming this helper validates that application. Reuse the user's established medium/software preferences and record them with the project.

The helper manages mechanical evidence for a drawing production; the agent supplies creative plans and actual artwork. All registered paths are relative to the project root and must resolve inside it. Preserve original media and previous revisions. JSON uses UTF-8; all shot intervals are zero-based and end-exclusive.

## Project record

`project.json` has `schema_version` equal to 1, `mode` equal to `create`, `recreate` or `edit`, `brief_file`, `canvas` with positive integer `width`, `height`, and a positive rational `fps` string, `source_assets`, `design_files`, ordered `shots`, `changes`, `audio`, `source_analysis`, and `final_video`.

Each source asset has an `id`, `path`, and `sha256`. Initialization copies supplied files into the project's `sources` folder; it never writes to the originals. Creation needs no source asset. Source-based modes require source material and a source-analysis file before final completion. A native Krita input can be analyzed as a document rather than a video.

`design_files` lists actual design and style documents or images. `source_analysis` is a path to actual source observations when relevant. `changes` records `id`, `scope`, `start_frame`, optional `end_frame`, `affected_shots`, and the reason for any preserved dependent content. Final completion checks change IDs, frame ranges and shot coverage mechanically; the agent reviews causal correctness.

`audio` contains `decision` equal to `silent`, `preserve`, `create` or `modify`, a contextual `reason`, and `assets`. Each asset has `path`, `start_frame`, and `duration_frames` on the authoritative output timeline. Extra stem, voice, speech-window, provenance and mixing fields may be added. `final_video` is the actual output file path, not a plan for an export.

## Shot record

Each ordered shot contains:

- Unique `id`, global output `start_frame`, positive `frame_count`, `intent`, and `motion_note`.
- `motion` equal to `drawn`, `hold`, `camera`, or `source`. Use `drawn` for changing-pose/form animation; `source` denotes deliberate reused source material. The choice is a factual production description.
- `change_ids`, optional source/output mappings and continuity notes, and an `inbetween_policy` with `decision` equal to `required` or `not-needed` plus `reason`.
- `drawings`: records with unique `id`, `role` equal to `key`, `breakdown`, `inbetween`, `hold` or `source`, `origin` equal to `canvas`, `imported`, `generated` or `source`, `motion_note`, `rough` PNG path, and a `final` PNG path when finished. Additional references, layer roles and provenance belong here or in adjacent production notes.
- `exposures`: ordered records with local `start`, `end`, and `drawing_id`. Cover exactly `[0, frame_count)` without gaps or overlap. Held drawings occupy longer exposures; do not invent new drawing identities for identical exposures.
- `krita`: `rough` and `final` native `.kra` paths as relevant to the requested stage; `pencil_test` is the actual rough preview path.

PNG records are full-canvas projections for timing and comparison. Native `.kra` documents retain the useful editable layers. The helper does not reconstruct layers from flat PNGs. Distinct drawings must depict the planned movement; different hashes alone do not prove it. A drawn-motion shot needs multiple rough drawings; required inbetweens need actual corresponding drawing records. No arbitrary professional-quality threshold is inferred from their count.

For camera animation, layer-specific timing or compositing beyond flat projections, preserve the native operations and export full-canvas projections that match the intended result. Generated onion previews are reference files, not new drawing evidence. Source-only reuse is permissible in an edit when consistent with the request, and must be identified as reuse.

## Reviews and fingerprints

Save `shots/<shot-id>/reviews/rough.json` and `final.json` for the stages actually reviewed. Each contains `status` equal to `pass`, `revise` or `pending`, `fingerprint` from the helper, nonempty `observations` recording actual findings, and `issues`. A pass record has no unresolved issues. Additional frame references, correction history and reviewer information are useful.

Call `fingerprint` after the reviewed inputs and exports are saved. It binds the brief, project settings, source and design assets, shot plan, exposure timing, stage drawings, native document and pencil test. A final fingerprint also binds final video, source analysis, audio assets and output-wide timing/change decisions. Changing these inputs invalidates the recorded review. Never calculate a new fingerprint and carry an old review forward without reviewing the changed material.

`validate --stage rough --require-complete` checks a deliverable rough animation, native rough files and current rough review records. Final completion also requires a reviewed rough stage, final artwork and native documents, design references, final output, contextual audio decision, and source observations for source-based work. Source-only reused shots can retain their source mappings without a newly created native drawing document. Preliminary `validate` reports missing items without claiming a production stage complete.

The `.kra` check only recognizes basic ZIP container structure; reopening in Krita and inspecting actual layers and timing remain necessary. Complete-stage checks use FFprobe for pencil-test timing and final-video frame count, rate, dimensions and required audio-stream presence. Actual visual playback and listening remain necessary. No helper-generated report certifies artistic quality or truthful review.

## Prepared references and pencil tests

`prepare` writes versioned contact sheets, an exposure CSV, and tinted neighbor-drawing reference images under `shots/<shot-id>/prepared/<stage>-<fingerprint-prefix>`. It preserves originals and does not mark review passed. Onion previews work best with transparent rough drawings; opaque backgrounds can hide the references. Use native onion skins or a deliberately prepared transparent reference layer when needed.

`pencil-test` encodes the rough exposures as a silent, fixed-rate preview. It materializes the exact exposure sequence in a versioned preview folder carrying an input-signature prefix, verifies decoded frame count with FFprobe, then registers the resulting preview path. Pixel padding to even dimensions may be applied for H.264. It does not create motion, add audio, or generate a native Krita file. A missing encoder/probe leaves the task incomplete with an explicit error.

Set `--workers 1` on `prepare` for sequential processing; the default is at most four CPU workers. Independent reference rendering uses processes. Decisions, dependent drawing, and Krita input are not parallelized by this helper.

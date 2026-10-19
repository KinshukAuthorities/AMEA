---
name: amea-edit
description: Edit existing 2D or 3D anime animation, including changed motion, inserted material, persistent later changes, style, timing, text, framing, effects, and contextual audio while preserving unaffected content.
---

# AMEA Animation Editing

Read [source analysis](../amea/references/source-analysis.md), [editing and styling](../amea/references/editing-and-styling.md), and [review](../amea/references/review.md). For 2D use [production](../amea/references/production.md), with [Krita](../amea/references/krita.md) and the [drawing helper format](../amea/references/project-format.md) only when applicable; for 3D use [AMEA 3D](../amea-3d/SKILL.md). Read [asset generation](../amea/references/asset-generation.md) for required new assets and [audio](../amea/references/audio.md) for sound. Reuse established medium/software choices and ask only for missing preferences.

Interpret the requested changes in the full context of the existing animation. Infer implementation choices, preservation of unaffected content, continuity, synchronization, and requested output delivery without making the user repeat them. A source video, native drawing or scene, frame sequence, or existing AMEA project can supply the starting point.

Map each change's affected interval and causal consequences. A persistent change continues through every dependent later frame or shot until its endpoint. Inserted sequences can coexist with those changes. Reconsider subsequent staging, interactions, visible state, lighting, occlusion, sound, captions, and narrative consequences rather than applying an isolated replacement and reverting automatically.

Reuse unaffected footage and sound where appropriate. Rebuild affected action through layouts, key poses, breakdowns, inbetweens, and a reviewed pencil test. Preserve separate editable layers for changed content, masks, background repair, and compositing where useful. A general style or finishing change may use a consistent processing method without requiring new poses when motion is unchanged. Do not force a full redraw for a simple requested edit.

Keep source time and output time separate. Define how every reused interval, replacement, insertion, removal, hold, and retime maps to the output timeline. Update later visuals, speech windows, effects, music, and captions through that same mapping. Allow duration to change when needed unless the user requires a fixed runtime; resolve that constraint before finishing dependent drawings.

Decide sound from the edit and surrounding context. Preserve speech when possible; new speech must fit measured timing and avoid unintended overlap with existing dialogue. Audio is not compulsory. Editing baked-in text requires repairing the image under it; subtitle edits alone do not remove visible lettering.

Initialize mode `edit`, or create a new revision of an existing project. Record change IDs, scope, affected shots and preservation decisions. Inspect the edited sequences and their boundaries, then the whole output. Deliver editable affected work and the requested assembled result with accurate reuse and drawing provenance.

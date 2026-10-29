# Review and completion

Use [computer-vision review and repair](visual-review-and-repair.md) as the primary animation-quality gate. Inspect actual playback and consecutive rendered frames, correct observed defects in native work, and visually retest the affected sequence. Code measurements support that process; they cannot close a visible issue by themselves.

Apply these checks to the resolved [canonical workflow](workflow-selection.md). Apply drawing checks to the selected 2D documents. Do not fabricate a native file or validator pass for an application that was not used.

Review the actual artifacts at each requested stage. Automated checks can find corrupt images, missing files, repeated pixel content, timeline gaps, stale records, and absent deliverables. They cannot establish good drawing, appropriate performance, convincing motion, or faithful understanding.

Use [first-delivery acceptance](first-delivery.md) to check coverage against the original request, prove the actual production route before scaling, and reconcile shot-boundary state. A review pass is specific to the requested stage and current inputs. The optional `delivery_gate.py` checks declared acceptance records across software; it does not replace the perceptual review.

## Rough review

- Compare the moving sequence against the recorded [performance intent](brief-to-performance.md): energy, pacing, meaningful actions/responses, emotion or visual purpose, camera motivation and coverage. Revise missing, repetitive or unreadable performance even when no numerical bug exists. Preserve intentional quietness and source fidelity.
- Confirm that the requested action is visible through the intended changes in drawings. Examine pose, form, expression, overlap and depth where relevant. Camera motion or pixel differences alone are insufficient evidence of articulated animation.
- Compare actual keys, breakdowns and inbetweens against their motion notes. Check spacing, contacts, arcs, volume, perspective and consistency against the fixed design references.
- Inspect the clean pencil test at speed, then frame by frame and with onion references. Check boundaries and transitions as well as the center of the shot.
- Record intentional holds and camera-only intervals explicitly. Do not impose an arbitrary minimum drawing count, and do not excuse a frozen action as a hold after the fact.
- Save concrete observations, identified issues, corrections and the reviewed artifact identities. A helper must never fill perceptual observations or mark this review passed automatically.

When [parallel workers](parallel-production.md) are available, review completed real intervals while independent work continues. Give the reviewer current artifacts, references and the brief without presupposing success. The coordinator reconciles observations, shared timing and shot boundaries; do not transfer an old pass to changed inputs or treat a worker completion message as visual evidence.

## Finish and whole-output review

Check cleanup fidelity, color and texture attachment, lighting, edges, background integration, text accuracy, and unwanted flicker. Review causally affected later shots and the beginning and end of inserted sequences. Compare preserved regions with their source when preservation matters.

Listen to the final mix while watching the exported output whenever audio is present. Check speech timing, intelligibility, intended overlaps, mouth timing, effects, cuts, and caption synchronization. An audio file existing on disk is not proof that it is audible or synchronized in the export.

Reopen native documents in the selected software and verify useful editing structure and timing. Check that external audio and references travel with the project. Inspect the final video with a probe and actual playback; file extension and successful encoder exit are insufficient.

## Evidence and honesty

Keep review records bound to current drawings, timing, native files and relevant inputs, including output/audio for final review. Use the cross-software `tools/delivery_gate.py` fingerprint command or equivalent revision-bound native evidence. The Krita helper's per-shot fingerprint format applies only to selected Krita work. Recompute and perform the affected review after changes; exporting references or calculating hashes does not count as reviewing them.

For the Krita-only helper, `structural_passed` means mechanical integrity and `recorded_reviews_current` means current pass records exist. Cross-software acceptance instead uses its own `recorded_acceptance_current` result; Blender transport reports native compilation only. None certifies truthful observations or artistic quality. Do not require an unrelated helper's fields to approve a different application. Reject transformed stills that fail the requested performance through actual visual comparison, even if structural checks pass.

If quality is insufficient, revise the affected drawings and dependencies. If a required capability is missing, deliver a truthful checkpoint with the remaining work identified. Do not label planning, generated stills, source re-encoding, or unreviewed roughs as a completed drawn animation.

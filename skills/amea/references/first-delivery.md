# First-delivery acceptance

Read this before production and again before delivery. The aim is to satisfy the initial brief through the agent's own internal tests and revisions, without making the user discover routine defects. A first delivery may require several internal iterations. Instructions cannot guarantee taste, production skill or capabilities the host does not provide.

## Keep the request connected to the output

Preserve the original request, subsequent corrections and supplied references in the project. Extract a compact list of acceptance requirements: requested stage, content and actions, design/fidelity, medium/software, duration/timing, framing, visual treatment, sound, preservation constraints and deliverables as relevant. Distinguish explicit requirements from inferred production choices. Resolve conflicts using the user's latest applicable instruction and keep unaffected earlier requirements.

For each material requirement record what would demonstrate success and where it will be checked in the actual artifact. Link it to shots/assets or output intervals. Keep one record with the existing brief/shot plan rather than creating competing specifications. Before delivery, compare that record against the original request again; a perfectly checked list can still omit a requested feature.

Reuse established preferences and reference authority. Infer reversible creative choices and routine production decisions. Ask one concise, bundled question only for missing essential choices or an actual access/scope decision. If the user delegates medium/software selection, choose suitably and proceed. An internal quality gate is not a request for repeated user approval.

## Demonstrate the actual production route early

Apply the test to the requested stage. A planning-only deliverable needs document review against the brief, not finished animation, an editor test or media export. A rough-only request proves the rough production and preview route without demanding cleanup, final materials or finishing. For a completed-animation request, test the finished method described below before scaling it.

Check the required path from inputs to native editable work to export and inspection. Package installation, a successful dependency doctor, attractive reference images or a static generated mesh do not prove that path. Verify usable controls for drawing/modeling, temporal consistency, required articulation/expression, contextual sound generation when needed, and real output review.

For animation production, test a short representative interval through the intended method and stage-appropriate visual treatment at useful delivery framing. Include the hardest relevant view, motion, deformation, interaction, expression or integration requirement. Also test a quiet or transitional interval when it exposes a different risk. Scale these tests to the task; do not build unrelated rigs or new movement for a finishing-only edit.

Inspect both the real moving result and the native editing structure. Judge identity and style at the views and framing the production will use; a neutral front view is insufficient when other views matter. Check that the chosen method can sustain the required consistency, not just produce one good image. For speech, test actual usable audio and timing rather than a text script. Prove required compositing, text, color/alpha and export behavior when they are a material risk.

If this test fails, correct the method or its inputs before scaling. Do not polish a known wrong design or multiply an unproven animation process across the whole sequence. A different supported tool or native repair may solve the problem within existing preferences; changing a user-mandated medium, software, provenance constraint or essential scope needs their decision. For unavailable models or blocked generation access, follow [asset generation](asset-generation.md) and wait for the user's route choice before switching methods or setting up another model. Preserve accepted work and continue independent tasks while resolving a blocker.

## Review the whole intended result

Use [brief to performance](brief-to-performance.md), [review](review.md) and [visual repair](visual-review-and-repair.md) for actual perceptual checks. At shot boundaries maintain the relevant state: design/proportions, scale, placement, direction, support/contact, visible changes, lighting, expressions, camera geography and sound. Use the ending state of one interval as the input to the next. A new worker, insertion or asset revision does not reset persistent state.

Check the actual exported deliverable against every acceptance requirement after integration. Watch the complete output when claiming a whole-output motion review; inspect consecutive-frame windows around risky events and every frame if that coverage was requested. Listen when sound is present. Review final framing, text and finishing after compression. Include the first/last frame, cuts, inserted boundaries and required loop seam. Convert frame-index conventions explicitly when combining tools; inclusive render endpoints and end-exclusive shot intervals are different contracts.

Reopen native work with its linked assets and verify useful editability. Run the applicable mechanical checks for the chosen software and requested stage. Review a copy or relocated delivery folder when testing portability rather than mutating the working master. Reviewers receive the original brief, canonical references and current output without being told it has passed. Use a read-only worker when available; otherwise make a separate comparison pass against the original request.

Internal corrections continue before delivery. A valid file, high polygon count, many keys or a positive worker summary cannot compensate for a missing requirement or visible failure. Do not average away a failed requirement with scores in unrelated categories. Honor intermediate-stage requests; do not insist on finishing a video when only a plan or rough was requested.

## Optional cross-software acceptance record

For multistep jobs or several explicit requirements, `tools/delivery_gate.py` checks a small project-local `delivery.json`. The record supplements native inspection and existing drawing/scene helpers. It does not draw, animate, listen, interpret the request or certify artistic quality. An equivalent compact record is enough for a small edit; the actual acceptance comparison still applies.

| Field | Contract |
| --- | --- |
| `schema_version`, `stage` | Version `1` and the actual requested deliverable stage. A rough-stage pass is not a final-production claim. |
| `request_files` | Nonempty list of project-relative files preserving the current user request and applicable corrections. |
| `requirements` | Nonempty list with unique `id`, `text`, observable `acceptance`, and nonempty `checks`. Optional `origin` distinguishes user requirements from inferred decisions. Declare `frame_ranges` for required temporal coverage. |
| `artifacts` | Unique `id` and project-relative `path` for real, nonempty request-relevant files: native work, references, previews, outputs, sound or evidence reports. Include linked dependencies in relevant reviews. |
| `reviews` | Unique `id`, `method`, `requirement_ids`, `artifact_ids`, optional `issue_ids` and `frame_ranges`, `status`, actual `observations` and an input `fingerprint` for a pass. Methods are `visual`, `playback`, `listening`, `reopen`, `mechanical` or `document`. |
| `issues` | List of material defects with unique `id`, `description`, `requirement_ids`, required retest `checks` and `artifact_ids`, optional `frame_ranges`, and `state` equal to `open` or `resolved`. A resolved issue names `resolution_review_ids` whose current observations cover its required methods, artifacts and declared ranges. |

Each requirement's `checks` names the methods it actually needs. Visual appearance requires visual inspection; motion requires playback, with consecutive frames for diagnosis; sound requires listening; native editability requires reopening. Document review is suitable for a planning deliverable, and mechanical review for measured constraints. Choose methods from the requirement rather than checking everything indiscriminately. Store historical failed reviews outside the current acceptance list; retain material unresolved issues in `issues`.

`frame_ranges` is a nonempty list of two-integer intervals on the authoritative output clock, zero-based and end-exclusive. Map shot-local or source timestamps to that clock before recording them. Current reviews for each required method must together cover all declared required intervals without gaps. Expanded review ranges change the fingerprint and require a new real inspection. When ranges are omitted, the helper checks method coverage only; it does not establish how much footage was inspected. Frame ranges do not prove spatial coverage or truthful playback/listening.

Run `python tools/delivery_gate.py fingerprint <delivery.json> --review <review-id>` after saving the inputs. Perform the real review, record its observations and fingerprint, then run `python tools/delivery_gate.py check <delivery.json>`. Fingerprinting never creates a pass or observations. The check fails on missing evidence, uncovered checks/ranges, stale reviews or unresolved material issues. Changes to the brief, acceptance criteria, reviewed files, inspection range or issue/retest contract invalidate the affected fingerprints. A new hash cannot make an old observation current.

The report's `recorded_acceptance_current` means only that declared checks have current records. The agent must still verify that the request was captured fully, the methods were appropriate and the observations truthful. Keep the record proportional; do not let paperwork replace production or visual judgment.

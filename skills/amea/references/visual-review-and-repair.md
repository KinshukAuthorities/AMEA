# Computer-vision review and repair

## Visual evidence comes first

Use ChatGPT's visual understanding of actual playback and rendered images as the primary animation-quality assessment. Inspect the real selected application's preview and the exported result. Automated math, pose estimates, optical flow, pixel differences, frame counts and successful encodes can nominate issues or validate mechanics, but they cannot establish correct anatomy, likeness, weight, emotion or contact.

Review motion at intended speed, then inspect slow or consecutive-frame windows around meaningful actions, fast movement, direction changes, close interactions, pose extremes, support transitions, landings, cuts, and persistent edits. Check lead-in and recovery, not just the central key. Uniformly spaced still samples alone can miss a brief deformation. If complete frame-by-frame review is requested, inspect every frame and track coverage honestly.

Use canonical design references alongside neighboring frames. Inspect silhouettes, normal color renders, and relevant crops. For diagnosis, use unblurred previews, alternate inspection views, isolated layers or objects, and optional skeleton/wireframe overlays as needed. Label diagnostic views separately and also inspect the actual final camera/composite. Blur, occlusion and effects can hide faults.

## Detect visible failures

Trace each relevant form through adjacent frames and its attachments. Look for reversed or twisted segments, implausible bends, lost volume, pinched joints, stretched slivers, detached parts, incorrect rigid attachments, slipping or floating support, body intersections, missed contact and inconsistent motion direction. Check foot/ankle/shin/knee/hip orientation when those structures exist; a mathematically constant bone can still drive a badly folded mesh.

For 2D, inspect changing construction and silhouette, joint direction, volume, perspective, feature placement, identity, line/color consistency, depth order and contact. For 3D, also inspect skin-weight leakage, pole-vector flips, joint axes, bind transforms, interpolation wraps, texture/UV stretching and deformed geometry. The method of diagnosis depends on the subject; characters and anatomical structures are not mandatory.

Judge performance as well as defects: preparation, force, balance, action spacing, reaction, recovery, gaze, expression, camera readability and temporal continuity. Compare energy, rhythm, variety and emotional or visual purpose with the recorded [brief and performance intent](brief-to-performance.md). Repeated neutral poses, missing responses or weak staging can be wrong even without a technical artifact. Distinguish deliberate stylization, smear drawings, squash/stretch or unsupported motion from unintended faults.

Optional tracking/optical-flow or pose tools can help identify discontinuities and suspect intervals, but anime proportions, occlusion, blur and stylization can make those estimates unreliable. Confirm candidates against the actual images. Do not install another vision model merely to claim computer vision was used when the session already provides suitable visual inspection.

## Repair loop

1. Record the visible issue, frame/time interval, affected form, reference and rendered evidence. Keep observations separate from a suspected cause.
2. Inspect surrounding frames and, if needed, another diagnostic view to locate the cause. Do not assume every bad pose is a skin-weight problem or every contact miss is an IK problem.
3. Correct the native artwork, mesh, topology, weights, rest/bind transforms, axes, constraints, targets, staging, timing or camera as appropriate. Preserve a previous revision and accepted unaffected work.
4. Invalidate the affected output and dependent later material. Re-render a short corrected window before spending time on the full export. Keep audio, effects and captions aligned if timing changed.
5. Visually compare the corrected sequence with the references and the failed version. Recheck the neighboring transitions and speed; a repair can move a defect to an adjacent frame.
6. Keep the issue open until the corrected result has been inspected. Continue the repair loop for actionable failures, then review the encoded result after finishing. Do not deliver a known visibly broken sequence as completed work. If a capability prevents further correction, label the actual stage and precise unresolved defect.

These are internal production checks, not automatic requests for user approval. Do not make the user diagnose an issue the agent can inspect and fix itself. Do not hide an unresolved defect behind a passing script report or claim that all bugs are impossible.

If consecutive retests reproduce substantially the same failure, stop full exports and ineffective parameter cycling. Revisit the actual cause, compare diagnostic views, and test a materially different correction on a short interval before scaling again. A changed production method also needs the [representative route test](first-delivery.md). Preserve accepted assets and unaffected work. If available methods cannot resolve the issue, state the concrete capability gap rather than spending the session repeating the same failed approach.

## Preserve truthful review records

Choose each new test to settle a concrete production decision. Inspect existing pixels first; reuse sufficient evidence instead of rerunning passed software checks. For a weak drawing, a large affected view and its neighboring construction may be decisive. For a weak launch or turn, use the real consecutive interval and intended timing. More reports, a broad mechanical suite or repeated full exports do not improve artistic evidence. Preserve the specific failed observation and make a cause-led local correction.

Bind contact sheets and extracted review frames to their actual source revision. After a repair, retain old evidence as clearly historical or regenerate only the affected sheet; do not let a stale thumbnail appear to show the current success or failure.

Record the actual visual tool/method, input or output identities, inspected frame ranges, reference images, observations, evidence crops where useful, issue state, correction and retest. A resolved issue needs observations of the new output. Do not copy old review results onto changed frames or let helpers create perceptual pass records automatically.

A review worker may inspect stable exports while another worker produces independent material. Follow [parallel production](parallel-production.md): read-only review inputs, exact artifact revisions, coordinator reconciliation and invalidation after changes. Inspect transitions between independently produced intervals as well as their interiors. Worker confidence or a completion summary is not a substitute for observing the result.

Successful encoding and finite bone transforms are separate mechanical evidence. Actual listening is still needed when judging sound. If only sampled frames were inspected, say so; do not claim full playback, complete coverage or subjective audio review.

# Animation-ready 3D assets

## Design and coordinate contract

Fix canonical references before generating detail. Record silhouettes, proportions, landmarks, palette, construction, material treatment, and required views and deformations. Compare actual neutral and representative expressive renders against those references. Inspect silhouette without texture as well as the lit result. More polygons cannot repair incorrect structure or likeness.

Record world up, model forward, handedness, units, ground plane, origin, and object/rig transforms. Convert geometry, normals, references, and rigs consistently. Determine alignment from the actual asset rather than format assumptions. Inspect disconnected fragments before normalizing bounds: a remote fragment can distort the apparent center and scale.

Keep render detail separate from deformation topology. Dense inferred surfaces may need retopology, joint loops, thickness, attachments, and lower-cost deforming meshes. Preserve original sculpts while making reviewed LODs. Evaluate each LOD at final framing and through motion. Viewport proxies need not be render substitutes.

## Optional local geometry generation

The optional image-conditioned backend creates static geometry from an actual reference image. Provide clean references with real alpha where isolation is intended. A plain-looking background is not necessarily transparent. Inspect image and alpha separately. A single view cannot establish hidden geometry; record inferred surfaces as inferred and correct them when additional references are available.

Use consistent modeling views and coordinate conventions. Generate separate parts only when helpful; fit them by landmarks and consistent scale, and repair attachment seams. Overlapping disconnected surfaces do not create a clean deformable join. Record seed, input identity, settings, tool/checkpoint identity, and outputs. Reuse accepted parts rather than regenerating the whole asset for a local defect.

Inspect finite vertices, bounds, normals, components, holes, thin sheets, and self-intersections. Remove inference floaters when appropriate to a single connected form; preserve valid separate parts. Watertightness is useful for some assets, but is not a universal requirement or a quality certificate.

Known hierarchical-decoder issues: fractional voxel dimensions constructed in an integer dtype can collapse query coordinates; use float32 before converting queries to inference dtype. NaN-filled unqueried refinement cells can create artificial marching-cubes sheets; preserve coarse inside/outside signs through trilinear refinement. The optional compatibility patch helper checks this source layout before modifying it. Keep original licenses and prominent modification notices. Do not apply old patches blindly to changed upstream code.

On a memory-limited GPU, use sequential inference, CPU offload, and bounded surface-query chunks. Check the actual execution device after attaching offload hooks. The lightweight pipeline may need an explicit `components` mapping. Reuse existing model weights and VAE; avoid fetching an unrelated model to work around a known compatibility defect.

## Materials and expression

Image projection can smear side views, duplicate highlights, distort features, and reveal seams. Check UVs, alpha edges, rear/side views, lighting, and moving joints. Use stable UVs and deliberate painted or procedural materials where projection fails. Keep textures and details attached to the moving form.

Plan the geometry and controls needed for expressions and fine articulation. A painted neutral face or a named scalar property does not demonstrate expressive geometry. Use appropriate gaze, eyelid, mouth, hand, or component controls when required, and test actual visible results. Speech-driven mouth animation requires measured speech timing.

## Rigging and deformation

Fit joints to the actual form and derive chain lengths from its rest pose. Preserve hierarchy, local axes, bind matrices, and scale. Do not transfer unrelated fixed proportions into a new asset. Keep object motion, rig motion, deformation, facial controls, and materials separate enough to edit and test.

Partition influences by anatomical or mechanical region before joint blending. Euclidean nearest-bone assignment can cross to an adjacent unrelated surface. Use constrained regions or surface connectivity, normalize weights, and remove accidental control-bone influences. Smooth weights along the surface without spreading them into another region or erasing intentional rigid behavior.

Blend along actual chains and attachment transitions. Select linear or dual-quaternion deformation by observed behavior; neither repairs wrong influences. Preserve rigid parts deliberately. Use corrective shapes, improved topology, extra controls, or pose deformation when basic skinning collapses volume.

Test representative extremes before a long bake. Inspect surfaces as well as skeletons: pinching, stretched slivers, twisting, separated attachments, inverted faces, and silhouette loss can exist while every bone retains its length. Save the accepted asset cache independently of shot animation.

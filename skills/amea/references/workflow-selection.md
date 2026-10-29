# Canonical workflow selection

This is the routing authority within AMEA. Apply the user's explicit requirements and preserve existing work first. Then use this policy to select one production route. Other references explain parts of that route; they are not competing defaults.

## Default: constructed, authored 2D drawings

For a new request to make anime without a specified medium, select **drawn 2D**. If no software is specified or inherited from the project, select **Blender Grease Pencil**. State these working choices briefly and proceed; do not require a preference questionnaire to activate the default.

The default authoring method is agent-authored editable contours, using construction guides and changing whole poses, transferred through the native API. Programmatic path entry is allowed unless the user excludes it. It is not physical stylus drawing, raster tracing, a generated image sequence or a rendered 3D character. An API helper transfers the art; the agent remains responsible for construction, posing, expression and visual repair.

Use [drawn anime construction](drawn-anime.md) as the 2D performance authority and [Blender 2D execution](blender-2d.md) for that default implementation. The production order is: brief and design authority → relevant-view keys → reviewed keys → breakdowns and inbetweens → consecutive native finished-method test → targeted repair and retest → remaining production → final output/native review and delivery. Use this same construction and review discipline for new drawn movement in creation, reconstruction and editing.

## Selection boundaries

| Request or project context | Selected route |
| --- | --- |
| New anime request, no medium/editor | Drawn 2D, Blender Grease Pencil, authored contours. |
| “2D anime that looks 3D,” depth, changing camera perspective | Drawn 2D with constructed views, foreshortening and parallax. Camera wording alone does not select rendered 3D. |
| Explicit other 2D editor | Same drawn construction/performance workflow through that editor's supported native tools. Read its execution guide only when selected. |
| Explicit 3D animation | Separate [3D route](../../amea-3d/SKILL.md). Reuse the chosen software; ask for it only if still essential and unspecified. |
| Edit or continue existing native work | Preserve its medium, software, accepted assets and unaffected performance unless conversion is requested. Apply current construction/review to new drawn movement. |
| Supplied raster artwork or source video | Inspect its role and preserve permitted useful material. An attachment does not select generated-frame production, tracing, a cutout rig or a different medium. |
| Explicit generation, cutout/rigged 2D, tracing, or direct canvas-only method | Follow that specific method within available capabilities and authorization; state its actual production method. It is an explicit alternative, never an automatic fallback. |

Image generation, video generation, 3D asset generation and tracing are **not prerequisites or fallback engines for the default 2D route**. Supplied reference images may guide design. Create missing construction references with the authored drawing workflow by default. Invoke another generation method only when the user selects it or explicitly authorizes it as an alternative. A missing generator, account, model or paid service must not block an otherwise available authored 2D route.

Likewise, do not switch from authored contours to slow simulated freehand input, force a Krita-only evidence format onto Grease Pencil, or render a 3D character just because another reference describes those tools. Respect an explicit drawing restriction; if the host cannot perform it, name that capability gap instead of mislabelling a different method.

## One contract for the active production

Record `workflow_id: drawn-2d`, medium, software, authoring method, reference authority and output clock in the project brief for the default route. For another selected route record its actual method. Record whether a choice came from the user, the existing project or the documented default. Workers and later sessions inherit that contract; they do not independently choose a backend. A method change is deliberate, scoped and subject to the user's constraints.

Within the package, resolve 2D routing questions with this file, construction/performance questions with `drawn-anime.md`, and Blender transport questions with `blender-2d.md`. General production, runtime, asset and review references supplement those choices. Their conditional instructions apply only after the relevant method has been selected. The Krita helper format and 3D asset-generation instructions do not override this default.

`CHATGPT-AMEA.md` is generated from the current skill sources by `tools/build_package.py`; it is the same workflow in consolidated form, not a second version to choose. Distribute and load files from one current bundle. Do not combine a stale copied prompt with current skills or hand-edit the generated file as a separate policy. Rebuild it and the archive after source instruction changes.

The default provides a repeatable production method, not a guarantee of artistic taste or skill. A successful native compile, many drawings or a passed mechanical check cannot replace the actual visual and motion gates. Preserve unresolved defects and report the real deliverable stage if the intended result cannot be completed.

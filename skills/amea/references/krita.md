# Krita execution

## Capability and method

Discover the installed Krita version, actual host controls, and accessible project location. The helper's `doctor` locates executables; it does not establish that an agent can inspect or operate the GUI. Verify app access with the current host's supported tools. Follow that host's computer-use skill and permissions. Use observed controls and current canvas coordinates; do not replay assumed coordinates across changed layouts.

For direct drawing requests, draw on Krita's canvas through supported input, keeping strokes and geometry appropriate to the current view. Do not silently replace a requested canvas workflow with imported artwork. For workflows that permit externally produced art, use Krita for editable assembly and correction, and describe which drawings were imported. A native `.kra` containing imported images alone is not evidence of canvas drawing.

If GUI control or a required integration is unavailable, preserve the brief, plan, drawings already produced, and next action. State the specific missing capability. A browser-only chat cannot operate desktop Krita merely by receiving these instructions. Do not install a remote-control service, download a model, or configure a new backend without the applicable authorization.

## Workspace and drawing

Create a shot document at the planned dimensions, color space, and frame rate. Select the Animation workspace or expose the Animation Timeline and Onion Skins dockers. Keep backgrounds and references separate from the transparent animated paint layers. A white painted background is opaque and can obscure onion references; Krita's canvas background can supply a viewing background separately.

Create actual animation frames on the intended layers. A selected empty timeline position is not automatically a new drawing. Confirm whether the chosen operation creates a blank or duplicates an existing exposure. Distinguish an intended held exposure from a duplicate drawing that still needs alteration. Record zero-based shot frames consistently with the project timing.

Enable onion skins for the animated layer and choose useful earlier and later drawing offsets, tint and opacity. Inspect the actual visible overlays while correcting poses. Toggle references and onions off for clean playback. Rendering or photographing an onion overlay is review evidence, not final artwork. If another tool produces the drawings, pass clean source drawings and separately labeled onion previews; do not accidentally bake the tinted references into the result.

Keep roughs, clean lines, color, and effects editable using an appropriate layer structure. Use incremental shot revisions before substantial corrections. Avoid changing the active document while another process operates it.

## Import, audio and export

When importing a PNG sequence, use File > Import Animation Frames and verify numeric ordering, start frame, spacing, and the document frame rate. For irregular drawing exposures, import a full timed sequence or establish each exposure explicitly; a single uniform step cannot express arbitrary timing. Confirm playback against the exposure sheet after import. Source video import can change timing and consume substantial memory; compare it with the preserved source ledger.

Load the timing audio through the animation timeline's audio controls when needed. Krita stores a reference to the audio file; keep that file inside the delivered project and verify relinking after moving the project. Use external tools when a task needs multitrack mixing or other sound operations beyond the available Krita controls.

Save genuine native `.kra` documents. Reopen them and verify layers, frame positions, exposures, canvas, rate, and linked audio. Export a lossless frame sequence before final video encoding when practical. Confirm whether the export contains every output frame or only unique drawings; the latter requires an accompanying exposure sheet. Never assume a missing PNG means the image should be held unless timing specifies it.

Krita can render animation through FFmpeg. Verify the actual encoder and output settings. Include audio only when selected, check the full output duration and final frame, and play the exported file. Rendering success is separate from visual review.

## Automation and CPU use

Prefer a supported structured integration for repeatable timeline operations when it meets the user's chosen method. Krita's Python API runs inside Krita with the appropriate scripting support; ordinary system Python does not automatically expose `krita`. Verify methods and return values for the installed version. Keep custom integration code inside the workspace until installation is actually needed and authorized.

Batch independent hashing, thumbnails, onion-reference images, and media processing with bounded workers. Do not issue concurrent GUI drawing commands, mutate one document from multiple workers, or create independent inbetweens without shared pose and timing references. CPU parallelism does not make model generation or dependent drawing decisions inherently faster.

Official references: [timeline](https://docs.krita.org/en/reference_manual/dockers/animation_timeline.html), [onion skins](https://docs.krita.org/en/reference_manual/dockers/onion_skin.html), [frame import](https://docs.krita.org/en/reference_manual/import_animation.html), [audio](https://docs.krita.org/en/reference_manual/audio_for_animation.html), [rendering](https://docs.krita.org/en/reference_manual/render_animation.html), [scripting](https://docs.krita.org/en/user_manual/python_scripting.html).

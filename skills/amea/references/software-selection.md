# Medium and software preferences

Before creating production assets, establish the user's 2D/3D preference and the software to use. Reuse choices already supplied in the request, conversation, or project. Ask for any missing choices together in one concise question. Do not make the user answer again on every shot or continuation. A specific preference overrides an inference from attached media; supplying a video does not decide the workflow by itself.

If the user explicitly delegates a choice, select an appropriate available tool and record it. Do not silently treat an unspecified preference as delegation. While a necessary preference is pending, inspect supplied material, inventory tools, and preserve the brief; postpone dependent production decisions.

Save `preferences.medium`, `preferences.software`, and relevant version/tool paths in the project. Verify actual native file support, scripting or UI control, drawing or rigging capabilities, rendering, audio support, and export. Tool installation is not proof that the current AI host can operate it. Use the host's supported interface and respect the chosen production method.

Krita drawing and Blender scene helpers are optional implementations supplied with AMEA. Other software can be used through its supported native tools, scripts, or host controls. Adapt the workflow and editable deliverable to that software; do not generate a fake native document for an unsupported application or silently switch applications.

Reuse installed dependencies first. Install missing libraries into an isolated project environment when needed for the selected workflow. Do not install a whole editor, tensor framework, model checkpoint, or unrelated backend for a task that does not need it. Missing access, platform incompatibility, or a required paid service needs a precise explanation and an appropriate alternative or user decision.

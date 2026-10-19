# AMEA — Anime Engineer Anything

**Create, recreate, edit, and convert anime into 2D, 3D animations with ChatGPT.**

[![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Quick start](#quick-start) · [Capabilities](#capabilities) · [Workflow](#workflow) · [Requirements](#requirements)

Start with a idea description, reference images, an existing project, or a video. AMEA supplies the skills and instructions for a ChatGPT session that can control the computer, work with files, and inspect the result.

## Quick start

### 1. Get AMEA

Clone the repository, or choose **Code → Download ZIP** on GitHub:

```bash
git clone https://github.com/KinshukAuthorities/AMEA.git
cd AMEA
```

### 2. Load and Use AMEA

Give your ChatGPT session access to the repository and ask it to read the repository and all its skills.

### 3. Make your request

```text
Use AMEA: [your request]
```

Attach any source material and include your 2D/3D and software preferences when known. if not provided, then AMEA asks for missing essential preferences.

## Capabilities

| Task | What AMEA does |
| --- | --- |
| [Create](skills/amea-create/SKILL.md) | Develop an original animation from your request. |
| [Recreate](skills/amea-recreate/SKILL.md) | Rebuild supplied footage for you preserving details, timings, quality. |
| [Edit](skills/amea-edit/SKILL.md) | Apply requested changes, insert material, or edit timing, style, framing, text, effects, and sound and much more as requested. |
| [Convert to 2D or 3D](skills/amea/SKILL.md) | Recreate a source video in the requested animation format and apply your specified changes. |

For faithful recreation, it follows the source. For edits, it preserves unaffected content and carries persistent changes into later scenes. Sound is handled according to the request and context. You do not need to restate continuity, synchronization, review, or export.

## Workflow

```mermaid
flowchart TD
    request[Your request and optional source material] --> intent[Requirements, medium and software]
    intent --> assets[Design and assets]
    intent --> plan[Storyboard and animation planning]
    intent --> setup[Setup and sound planning]
    assets --> test[Test the chosen production method]
    plan --> test
    setup --> test
    test --> production[Create, recreate, edit or convert]
    production --> review[Inspect playback, sound and editable project]
    review -->|Needs correction| production
    review -->|Ready| delivery[Deliver the requested output and editable project]
```

Independent work can run in parallel when the host supports it. The agent reviews actual playback and frames, corrects visible issues, and retests before delivery. The work stays within your request, including when you ask only for planning or a rough version.

## Requirements

- A ChatGPT session with the computer, file, visual-inspection, and generation capabilities needed for the task.
- Your selected animation software. AMEA asks if you have not already chosen it.
- Python 3.10+ for the optional helpers; FFmpeg and FFprobe for helper-based media processing.

[`requirements.txt`](requirements.txt) is the single dependency file. The agent installs only what the chosen workflow needs like blender, krita, pytorch etc as per requirements.

For new 3D assets, **TRELLIS.2 is the preferred starting point** when suitable. The agent uses your supplied asset images or creates missing references, then tries the [official hosted generator](https://huggingface.co/spaces/microsoft/TRELLIS.2) where available.

If the required model is unavailable or online generation is blocked, the agent explains the blocker and asks you to choose the next route. Choices can include returning generated assets from prepared images, setting up local generation, or selecting another suitable method. It waits for that choice before proceeding with an alternative. See [asset generation](skills/amea/references/asset-generation.md) and [setup](skills/amea/references/runtime.md).

AMEA is a skill and helper package. The connected tools and production work determine the achievable result; instructions alone do not provide those capabilities.

## License

[MIT](LICENSE). External tools, models, and supplied assets retain their own licenses and terms.

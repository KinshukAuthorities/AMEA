#!/usr/bin/env python3
"""Build standalone AMEA instructions and an archive of authored bundle files."""

import re
import zipfile
from pathlib import Path


def build(root=None):
    root = Path(root).resolve() if root else Path(__file__).resolve().parents[1]
    skills = [root / "skills" / name for name in ("amea", "amea-create", "amea-recreate", "amea-edit")]
    documents = [folder / "SKILL.md" for folder in skills]
    documents += sorted((skills[0] / "references").glob("*.md"))
    sections = ["# AMEA — ChatGPT Animation Production Instructions\n\n"
                "For ChatGPT sessions with verified computer-control, visual-inspection and workspace tools. "
                "Load these instructions, then activate with `Use AMEA:` followed by the user's request. "
                "Choose original creation, reconstruction, editing, or a combination from intent. "
                "No source video is required for original animation. The included sections supply all "
                "skill instructions and references. Local helper scripts remain in the AMEA bundle. "
                "Overlap independent asset work, story/action/camera planning, setup, sound planning and review "
                "with actual available permitted workers. Coordinate shared revisions, dependencies, native-file "
                "ownership and desktop input. Infer performance intent from the brief and verify it in moving roughs. "
                "Track material request requirements, prove the actual method at the requested stage before scaling, "
                "and compare the delivered result against the original request after internal corrections. "
                "Read the canonical workflow-selection section first: new unspecified anime requests use authored "
                "drawn 2D in Blender Grease Pencil. Explicit user choices and existing project medium/software take precedence. "
                "Construction, changing poses and consecutive native review are the default; generation, tracing, cutout "
                "methods are explicit alternatives. Default authored 2D requires no generation service. "
                "If an explicitly selected generation method's required model or online route is unavailable, "
                "explain the blocker, ask which available alternative the user wants, and wait before switching "
                "methods, installing an inference stack or downloading a local model. Reuse an existing choice. "
                "Computer-vision review of actual playback and rendered "
                "frames is the primary quality check; code measurements only support it. Instructions do not grant editor control, media access, "
                "image generation, speech tools, credentials or paid-service access. No dependencies or weights are bundled.\n"]
    for document in documents:
        text = document.read_text(encoding="utf-8")
        if document.name == "SKILL.md":
            text = text.split("---", 2)[2].strip()

        def local_link(match):
            label, target = match.groups()
            if "://" in target or target.startswith("#"):
                return match.group(0)
            resolved = (document.parent / target).resolve()
            if resolved not in documents:
                raise ValueError(f"Unbundled instruction link in {document}: {target}")
            return f"{label} (included section `{resolved.relative_to(root).as_posix()}`)"

        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", local_link, text)
        sections.append(f"\n---\n\nIncluded section: `{document.relative_to(root).as_posix()}`\n\n{text.strip()}\n")
    prompt = root / "CHATGPT-AMEA.md"
    prompt.write_text("\n".join(sections), encoding="utf-8")
    files = [root / "README.md", root / "LICENSE", root / ".gitignore", root / "requirements.txt", prompt]
    for folder in (root / "skills", root / "tools", root / "tests"):
        files += [path for path in folder.rglob("*") if path.is_file()
                  and not any(part in {"__pycache__", ".work", ".runtime", "runtime", "vendor", "projects"} for part in path.relative_to(root).parts)
                  and path.suffix in {".md", ".py", ".json", ".yaml", ".txt"}]
    archive_path = root.parent / "AMEA.zip"
    temporary = archive_path.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(files)):
            archive.write(path, "AMEA/" + path.relative_to(root).as_posix())
    temporary.replace(archive_path)
    return {"standalone_instructions": str(prompt), "archive": str(archive_path), "files": len(set(files)), "bytes": archive_path.stat().st_size}


if __name__ == "__main__":
    import json
    print(json.dumps(build(), indent=2))

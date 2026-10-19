#!/usr/bin/env python3
"""AMEA project evidence, reference preparation, and silent pencil tests.

This helper does not draw, control Krita, synthesize sound, or judge artwork.
"""

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path


class ProjectError(ValueError):
    pass


def read_json(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".amea-", suffix=".tmp", delete=False) as stream:
        temp = Path(stream.name)
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def safe_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", value):
        raise ProjectError("IDs must contain only letters, numbers, underscores and hyphens")
    return value


def local_file(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ProjectError(f"Expected a nonempty project-relative path: {value!r}")
    root = Path(root).resolve()
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ProjectError(f"Path escapes the project: {value}")
    if not path.is_file() or path.stat().st_size == 0:
        raise ProjectError(f"Missing or empty file: {value}")
    return path


def local_output(root, value):
    root = Path(root).resolve()
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ProjectError(f"Output path escapes the project: {value}")
    return path


def sha256(path, cache=None):
    key = str(Path(path).resolve())
    if cache is not None and key in cache:
        return cache[key]
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    result = digest.hexdigest()
    if cache is not None:
        cache[key] = result
    return result


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def frame_int(value, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise ProjectError(f"Expected {'positive' if positive else 'nonnegative'} integer frames: {value!r}")
    return value


def fps_value(value):
    try:
        rate = Fraction(str(value))
        if rate <= 0 or rate > 1000:
            raise ValueError()
        return rate
    except (ValueError, ZeroDivisionError):
        raise ProjectError(f"Invalid frame rate: {value!r}")


def load_project(root):
    root = Path(root).resolve()
    data = read_json(root / "project.json")
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ProjectError("Unsupported project format")
    if data.get("mode") not in {"create", "recreate", "edit"}:
        raise ProjectError("Project mode must be create, recreate or edit")
    for dimension in ("width", "height"):
        frame_int(data["canvas"][dimension], positive=True)
    fps_value(data["canvas"]["fps"])
    return root, data


def find_shot(data, shot_id):
    safe_id(shot_id)
    matches = [shot for shot in data["shots"] if shot.get("id") == shot_id]
    if len(matches) != 1:
        raise ProjectError(f"Expected exactly one shot named {shot_id}")
    return matches[0]


def drawing_file(root, shot, drawing, stage):
    value = drawing.get(stage)
    if not value and stage == "final" and shot.get("motion") == "source":
        value = drawing.get("rough")
    return local_file(root, value)


def stage_fingerprint(root, data, shot, stage, cache=None):
    cache = {} if cache is None else cache

    def identity(value):
        if value is None:
            return None
        return {"path": value, "sha256": sha256(local_file(root, value), cache)}

    shot_plan = json.loads(json.dumps(shot))
    shot_plan["krita"] = {stage: shot.get("krita", {}).get(stage)}
    for drawing in shot_plan.get("drawings", []):
        if stage == "rough":
            drawing.pop("final", None)
    payload = {
        "mode": data["mode"], "canvas": data["canvas"], "brief": identity(data["brief_file"]),
        "designs": [identity(path) for path in data.get("design_files", [])],
        "sources": [{"id": asset["id"], **identity(asset["path"])}
                    for asset in data.get("source_assets", [])],
        "stage": stage, "shot": shot_plan,
        "drawings": [{"id": drawing["id"], "sha256": sha256(drawing_file(root, shot, drawing, stage), cache)}
                     for drawing in shot.get("drawings", [])],
        "krita": identity(shot.get("krita", {}).get(stage)),
        "pencil_test": identity(shot.get("pencil_test")),
    }
    if stage == "final":
        payload["rough_drawings"] = [identity(drawing["rough"]) for drawing in shot.get("drawings", [])]
        payload["output_timeline"] = [{key: item.get(key) for key in
                                       ("id", "start_frame", "frame_count", "source_ranges", "change_ids")}
                                      for item in data["shots"]]
        payload["changes"] = data.get("changes", [])
        payload["analysis"] = identity(data.get("source_analysis"))
        payload["audio"] = data.get("audio")
        payload["audio_files"] = [identity(item["path"]) for item in data.get("audio", {}).get("assets", [])]
        payload["final_video"] = identity(data.get("final_video"))
    return canonical_hash(payload)


def discover_executable(name, explicit=None):
    if explicit:
        candidate = Path(explicit).expanduser()
        if not candidate.is_file():
            raise ProjectError(f"Executable does not exist: {candidate}")
        return str(candidate.resolve())
    env_path = os.environ.get(name.upper())
    if env_path and Path(env_path).is_file():
        return str(Path(env_path).resolve())
    found = shutil.which(name)
    if found:
        return found
    candidates = []
    if name == "krita":
        candidates += [Path("C:/Program Files/Krita (x64)/bin/krita.exe"),
                       Path("C:/Program Files/Krita/bin/krita.exe")]
    if name in {"ffmpeg", "ffprobe"}:
        packages = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
        candidates += sorted(packages.glob(f"Gyan.FFmpeg*/*/bin/{name}.exe"), reverse=True)
    return next((str(path) for path in candidates if path.is_file()), None)


def doctor():
    return {"python": sys.executable, "cpu_count": os.cpu_count(),
            "default_workers": min(4, os.cpu_count() or 1),
            "pillow_available": importlib.util.find_spec("PIL") is not None,
            "executables": {name: discover_executable(name) for name in ("krita", "ffmpeg", "ffprobe")},
            "gui_control": "not tested", "drawing_quality": "not tested",
            "audio_generation": "not configured by this helper",
            "free_bytes": shutil.disk_usage(Path.cwd()).free}


def init_project(destination, mode, request_file, sources=(), width=1280, height=720, fps="24"):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ProjectError("Choose a new project directory; existing work will not be overwritten")
    if mode not in {"create", "recreate", "edit"}:
        raise ProjectError("Invalid project mode")
    frame_int(width, positive=True)
    frame_int(height, positive=True)
    rate = fps_value(fps)
    brief = Path(request_file).read_text(encoding="utf-8-sig")
    if not brief.strip():
        raise ProjectError("The brief file is empty")
    source_paths = [Path(path).resolve() for path in sources]
    if mode != "create" and not source_paths:
        raise ProjectError("This mode needs source material; original creation does not")
    for path in source_paths:
        if not path.is_file() or not path.stat().st_size:
            raise ProjectError(f"Missing or empty source: {path}")
    destination.mkdir(parents=True)
    for folder in ("sources", "design", "analysis", "shots", "audio", "exports"):
        (destination / folder).mkdir()
    (destination / "brief.txt").write_text(brief, encoding="utf-8")
    assets = []
    for index, source in enumerate(source_paths, 1):
        target = destination / "sources" / f"{index:03d}-{source.name}"
        shutil.copy2(source, target)
        assets.append({"id": f"source-{index:03d}", "path": target.relative_to(destination).as_posix(),
                       "sha256": sha256(target)})
    data = {"schema_version": 1, "mode": mode, "brief_file": "brief.txt",
            "canvas": {"width": width, "height": height, "fps": str(rate)},
            "source_assets": assets, "design_files": [], "shots": [], "changes": [],
            "audio": {"decision": "undecided", "reason": "", "assets": []},
            "source_analysis": None, "final_video": None}
    write_json(destination / "project.json", data)
    return {"project": str(destination), "status": "draft", "drawings_created": 0}


def check_exposures(shot):
    frame_int(shot["frame_count"], positive=True)
    drawings = shot.get("drawings", [])
    ids = [safe_id(drawing["id"]) for drawing in drawings]
    if not ids or len(ids) != len(set(ids)):
        raise ProjectError("Drawing IDs must exist and be unique within a shot")
    cursor = 0
    used = set()
    for exposure in shot.get("exposures", []):
        start, end = frame_int(exposure["start"]), frame_int(exposure["end"], positive=True)
        if start != cursor or end <= start or end > shot["frame_count"]:
            raise ProjectError("Exposure intervals must cover the shot exactly, in order, without gaps or overlaps")
        if exposure["drawing_id"] not in ids:
            raise ProjectError("Exposure references an unknown drawing")
        used.add(exposure["drawing_id"])
        cursor = end
    if cursor != shot["frame_count"]:
        raise ProjectError("Exposure timing does not reach the end of the shot")
    if used != set(ids):
        raise ProjectError("Unexposed drawings must remain outside the delivery drawing list")


def _inspect_image(path):
    from PIL import Image
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ProjectError(f"Drawing is not a PNG: {path}")
        rgba = image.convert("RGBA")
        rgba.load()
        return {"size": list(rgba.size), "pixel_sha256": hashlib.sha256(rgba.tobytes()).hexdigest()}


def check_kra(path):
    if path.suffix.lower() != ".kra":
        raise ProjectError("Native document must have a .kra extension")
    try:
        with zipfile.ZipFile(path) as archive:
            if "maindoc.xml" not in archive.namelist():
                raise ProjectError("Krita container has no maindoc.xml")
            if archive.getinfo("mimetype").file_size > 1024:
                raise ProjectError("Invalid Krita mimetype entry")
            if archive.read("mimetype").strip() != b"application/x-krita":
                raise ProjectError("Unexpected Krita container mimetype")
    except (zipfile.BadZipFile, KeyError) as error:
        raise ProjectError(f"Unrecognized Krita container: {error}")


def probe_video(path, ffprobe=None):
    executable = discover_executable("ffprobe", ffprobe)
    if not executable:
        raise ProjectError("FFprobe is needed to verify exported video")
    result = subprocess.run([executable, "-v", "error", "-count_frames", "-show_streams",
                             "-show_format", "-of", "json", str(path)],
                            capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise ProjectError("FFprobe failed: " + result.stderr[-1500:])
    info = json.loads(result.stdout)
    videos = [item for item in info.get("streams", []) if item.get("codec_type") == "video"]
    if not videos:
        raise ProjectError("Export contains no video stream")
    return info, videos[0]


def validate_project(root, stage="final", require_complete=False, workers=None):
    errors, warnings = [], []
    reviews_current = True
    cache = {}
    try:
        root, data = load_project(root)
        local_file(root, data["brief_file"])
        sources = data.get("source_assets", [])
        source_ids = [safe_id(asset["id"]) for asset in sources]
        if len(source_ids) != len(set(source_ids)):
            raise ProjectError("Source IDs must be unique")
        for source in sources:
            if sha256(local_file(root, source["path"]), cache) != source["sha256"]:
                errors.append(f"Source integrity mismatch: {source['id']}")
        for path in data.get("design_files", []):
            local_file(root, path)
        shots = data.get("shots", [])
        if not shots:
            (errors if require_complete else warnings).append("No animation shots have been supplied")
            reviews_current = False
        ids = [safe_id(shot["id"]) for shot in shots]
        if len(ids) != len(set(ids)):
            raise ProjectError("Shot IDs must be unique")
        cursor = 0
        stages = ["rough", "final"] if stage == "final" and require_complete else [stage]
        for shot in shots:
            label = shot["id"]
            if frame_int(shot["start_frame"]) != cursor:
                errors.append(f"{label}: output shot timing contains a gap or overlap")
            cursor = shot["start_frame"] + frame_int(shot["frame_count"], positive=True)
            try:
                check_exposures(shot)
                if shot.get("motion") not in {"drawn", "hold", "camera", "source"}:
                    raise ProjectError("A factual motion classification is required")
                if not str(shot.get("intent", "")).strip() or not str(shot.get("motion_note", "")).strip():
                    raise ProjectError("Shot intent and motion note are required")
                policy = shot.get("inbetween_policy", {})
                if policy.get("decision") not in {"required", "not-needed"} or not policy.get("reason"):
                    raise ProjectError("An inbetween decision and reason are required")
                roles = {item.get("role") for item in shot["drawings"]}
                if not roles <= {"key", "breakdown", "inbetween", "hold", "source"}:
                    raise ProjectError("Invalid drawing role")
                for item in shot["drawings"]:
                    if item.get("origin") not in {"canvas", "imported", "generated", "source"}:
                        raise ProjectError("Actual drawing origin is required")
                    if not item.get("motion_note"):
                        raise ProjectError("Every drawing needs a motion note")
                if policy["decision"] == "required" and "inbetween" not in roles:
                    raise ProjectError("Required inbetweens have no drawing evidence")
                if shot["motion"] == "source" and not shot.get("source_ranges"):
                    raise ProjectError("Source reuse needs actual source ranges")
                for mapping in shot.get("source_ranges", []):
                    if mapping.get("asset_id") not in source_ids:
                        raise ProjectError("Source mapping references an unknown source asset")
                for phase in stages:
                    paths = [drawing_file(root, shot, item, phase) for item in shot["drawings"]]
                    count = max(1, min(workers or 4, os.cpu_count() or 1, len(paths)))
                    with ThreadPoolExecutor(max_workers=count) as pool:
                        inspected = list(pool.map(_inspect_image, paths))
                    expected = [data["canvas"]["width"], data["canvas"]["height"]]
                    if any(item["size"] != expected for item in inspected):
                        raise ProjectError(f"{phase} drawing dimensions differ from the project canvas")
                    unique_pixels = len({item["pixel_sha256"] for item in inspected})
                    if shot["motion"] == "drawn" and unique_pixels < 2:
                        raise ProjectError(f"{phase} drawn-motion shot has fewer than two distinct drawings")
                    if unique_pixels < len(paths):
                        warnings.append(f"{label}/{phase}: identical drawings have separate IDs; check intended holds")
                    native = shot.get("krita", {}).get(phase)
                    if native:
                        check_kra(local_file(root, native))
                    elif require_complete and shot["motion"] != "source":
                        raise ProjectError(f"Missing {phase} editable Krita document")
                    if shot.get("pencil_test"):
                        preview = local_file(root, shot["pencil_test"])
                        if require_complete and phase == "rough":
                            _, preview_stream = probe_video(preview)
                            if (int(preview_stream.get("nb_read_frames", -1)) != shot["frame_count"]
                                    or fps_value(preview_stream.get("avg_frame_rate", "0")) != fps_value(data["canvas"]["fps"])):
                                raise ProjectError("Pencil-test timing differs from the shot exposure sheet")
                    elif require_complete and shot["motion"] == "drawn":
                        raise ProjectError("A changing-drawing shot needs its actual pencil test")
                    review_path = local_output(root, f"shots/{label}/reviews/{phase}.json")
                    current = False
                    if review_path.is_file():
                        review = read_json(review_path)
                        current = (review.get("status") == "pass" and not review.get("issues")
                                   and isinstance(review.get("observations"), list)
                                   and any(isinstance(item, str) and item.strip() for item in review["observations"])
                                   and review.get("fingerprint") == stage_fingerprint(root, data, shot, phase, cache))
                    if not current:
                        reviews_current = False
                        (errors if require_complete else warnings).append(f"{label}/{phase}: current recorded perceptual review is missing")
            except (ProjectError, KeyError, TypeError, ValueError, OSError) as error:
                errors.append(f"{label}: {error}")
                reviews_current = False
        if require_complete and stage == "final":
            if not data.get("design_files"):
                errors.append("Final production needs its actual design references")
            if data["mode"] != "create":
                if not sources:
                    errors.append("Source-based production has no source assets")
                local_file(root, data.get("source_analysis"))
            audio = data.get("audio", {})
            if audio.get("decision") not in {"silent", "preserve", "create", "modify"} or not audio.get("reason"):
                errors.append("A contextual audio decision and reason are required")
            if audio.get("decision") in {"preserve", "create", "modify"} and not audio.get("assets"):
                errors.append("The selected audio decision has no registered sound assets")
            for asset in audio.get("assets", []):
                local_file(root, asset["path"])
                if frame_int(asset["start_frame"]) + frame_int(asset["duration_frames"], positive=True) > cursor:
                    errors.append("An audio asset extends beyond the output timeline")
            changes = data.get("changes", [])
            change_ids = [safe_id(change["id"]) for change in changes]
            if len(change_ids) != len(set(change_ids)):
                errors.append("Change IDs must be unique")
            for shot in shots:
                if not set(shot.get("change_ids", [])) <= set(change_ids):
                    errors.append(f"{shot['id']}: unknown change ID")
            for change in changes:
                start = frame_int(change["start_frame"])
                end = cursor if change.get("end_frame") is None else frame_int(change["end_frame"], positive=True)
                if start >= end or end > cursor or change.get("scope") not in {"range", "persistent"}:
                    errors.append(f"Invalid change range: {change['id']}")
                affected = {shot["id"] for shot in shots
                            if shot["start_frame"] < end and shot["start_frame"] + shot["frame_count"] > start}
                if set(change.get("affected_shots", [])) != affected:
                    errors.append(f"Change shot coverage is incomplete: {change['id']}")
                for shot in shots:
                    if shot["id"] in affected and change["id"] not in shot.get("change_ids", []):
                        errors.append(f"{shot['id']}: missing applicable change {change['id']}")
            output = local_file(root, data.get("final_video"))
            info, stream = probe_video(output)
            if int(stream.get("nb_read_frames", -1)) != cursor:
                errors.append("Exported video frame count does not match the output timeline")
            if fps_value(stream.get("avg_frame_rate", "0")) != fps_value(data["canvas"]["fps"]):
                errors.append("Exported video frame rate differs from the output timeline")
            expected_size = [data["canvas"][key] + data["canvas"][key] % 2 for key in ("width", "height")]
            if [stream.get("width"), stream.get("height")] not in [expected_size, [data["canvas"][key] for key in ("width", "height")]]:
                errors.append("Exported video dimensions differ from the planned canvas")
            if audio.get("decision") in {"preserve", "create", "modify"} and not any(
                    item.get("codec_type") == "audio" for item in info.get("streams", [])):
                errors.append("Selected soundtrack is absent from the exported video")
    except (ProjectError, KeyError, TypeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        errors.append(str(error))
        reviews_current = False
    return {"structural_passed": not errors, "recorded_reviews_current": reviews_current,
            "stage": stage, "require_complete": require_complete, "errors": errors, "warnings": warnings,
            "artistic_quality": "requires actual visual review; not certified by this helper",
            "review_truthfulness": "not certified by this helper"}


def _onion_image(job):
    from PIL import Image
    previous, current, following, destination, size = job
    canvas = Image.new("RGBA", tuple(size), "white")
    for path, color in ((previous, (220, 50, 50)), (following, (40, 100, 230))):
        if path:
            with Image.open(path) as source:
                rgba = source.convert("RGBA")
                tint = Image.new("RGBA", rgba.size, (*color, 255))
                tint.putalpha(rgba.getchannel("A").point(lambda value: round(value * 0.28)))
                canvas.alpha_composite(tint)
    with Image.open(current) as source:
        canvas.alpha_composite(source.convert("RGBA"))
    canvas.convert("RGB").save(destination)
    return str(destination)


def prepare_references(root, shot_id, stage="rough", workers=None):
    from PIL import Image, ImageDraw, ImageOps
    root, data = load_project(root)
    shot = find_shot(data, shot_id)
    check_exposures(shot)
    drawings = {item["id"]: item for item in shot["drawings"]}
    order = list(dict.fromkeys(exposure["drawing_id"] for exposure in shot["exposures"]))
    paths = [drawing_file(root, shot, drawings[item], stage) for item in order]
    expected = [data["canvas"]["width"], data["canvas"]["height"]]
    for path in paths:
        if _inspect_image(path)["size"] != expected:
            raise ProjectError("Drawing canvas dimensions do not match the project")
    signature = canonical_hash({"stage": stage, "shot": shot,
                                "images": [sha256(path) for path in paths]})
    parent = local_output(root, f"shots/{shot_id}/prepared")
    parent.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix=f"{stage}-{signature[:12]}-", dir=parent))
    exposure_paths = [drawing_file(root, shot, drawings[item["drawing_id"]], stage)
                      for item in shot["exposures"]]
    jobs = [(str(exposure_paths[index - 1]) if index else None, str(path),
             str(exposure_paths[index + 1]) if index + 1 < len(exposure_paths) else None,
             str(destination / f"onion-{index:04d}-{shot['exposures'][index]['drawing_id']}.png"), expected)
            for index, path in enumerate(exposure_paths)]
    count = max(1, min(workers or 4, os.cpu_count() or 1, len(jobs)))
    if count == 1:
        onions = list(map(_onion_image, jobs))
    else:
        with ProcessPoolExecutor(max_workers=count) as pool:
            onions = list(pool.map(_onion_image, jobs))
    for offset in range(0, len(paths), 24):
        subset = paths[offset:offset + 24]
        sheet = Image.new("RGB", (4 * 256, ((len(subset) + 3) // 4) * 172), "#dddddd")
        painter = ImageDraw.Draw(sheet)
        for index, path in enumerate(subset):
            with Image.open(path) as source:
                rgba = source.convert("RGBA")
                background = Image.new("RGBA", rgba.size, "white")
                background.alpha_composite(rgba)
                thumb = ImageOps.contain(background.convert("RGB"), (248, 142))
                x, y = (index % 4) * 256, (index // 4) * 172
                sheet.paste(thumb, (x + 4, y + 4))
                painter.text((x + 4, y + 149), order[offset + index], fill="black")
        sheet.save(destination / f"contact-{offset // 24:03d}.png")
    with (destination / "exposures.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["shot", "start_frame", "end_frame_exclusive", "drawing_id", "role", "origin"])
        for exposure in shot["exposures"]:
            item = drawings[exposure["drawing_id"]]
            writer.writerow([shot_id, exposure["start"], exposure["end"], item["id"], item["role"], item["origin"]])
    manifest = {"stage": stage, "input_signature": signature, "workers": count,
                "onion_files": [Path(path).name for path in onions],
                "source_drawings": [{"id": item, "path": str(path.relative_to(root)), "sha256": sha256(path)}
                                    for item, path in zip(order, paths)],
                "purpose": "review references only; no drawings or review results were created"}
    write_json(destination / "manifest.json", manifest)
    return {"prepared": str(destination), "workers": count, "drawings_created": 0}


def pencil_test(root, shot_id, ffmpeg=None, ffprobe=None):
    root, data = load_project(root)
    shot = find_shot(data, shot_id)
    check_exposures(shot)
    encoder = discover_executable("ffmpeg", ffmpeg)
    probe = discover_executable("ffprobe", ffprobe)
    if not encoder or not probe:
        raise ProjectError("FFmpeg and FFprobe are both required for a verified pencil test")
    drawings = {item["id"]: drawing_file(root, shot, item, "rough") for item in shot["drawings"]}
    expected = [data["canvas"]["width"], data["canvas"]["height"]]
    if any(_inspect_image(path)["size"] != expected for path in drawings.values()):
        raise ProjectError("Pencil-test drawing dimensions do not match the canvas")
    signature = canonical_hash({"fps": data["canvas"]["fps"], "canvas": data["canvas"],
                                "exposures": shot["exposures"],
                                "images": {key: sha256(path) for key, path in drawings.items()}})
    parent = local_output(root, f"shots/{shot_id}/previews")
    parent.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix=f"rough-{signature[:12]}-", dir=parent))
    frames = destination / "frames"
    frames.mkdir()
    from PIL import Image
    for exposure in shot["exposures"]:
        with Image.open(drawings[exposure["drawing_id"]]) as source:
            rgba = source.convert("RGBA")
            background = Image.new("RGBA", rgba.size, "white")
            background.alpha_composite(rgba)
            rgb = background.convert("RGB")
            first = frames / f"frame_{exposure['start']:06d}.png"
            rgb.save(first)
            for frame in range(exposure["start"] + 1, exposure["end"]):
                shutil.copyfile(first, frames / f"frame_{frame:06d}.png")
    output = destination / "pencil-test.mp4"
    threads = str(min(8, os.cpu_count() or 1))
    command = [encoder, "-v", "error", "-nostdin", "-framerate", str(fps_value(data["canvas"]["fps"])),
               "-start_number", "0", "-i", str(frames / "frame_%06d.png"), "-frames:v", str(shot["frame_count"]),
               "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white", "-an", "-c:v", "libx264",
               "-threads", threads, "-crf", "18", "-pix_fmt", "yuv420p", str(output)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    if result.returncode:
        raise ProjectError("Pencil-test encode failed: " + result.stderr[-2000:])
    _, stream = probe_video(output, probe)
    if int(stream.get("nb_read_frames", -1)) != shot["frame_count"]:
        raise ProjectError("Pencil-test frame count differs from the exposure sheet")
    shot["pencil_test"] = output.relative_to(root).as_posix()
    write_json(root / "project.json", data)
    return {"pencil_test": str(output), "frames": shot["frame_count"],
            "audio": "silent timing preview", "review_status": "not reviewed by this helper"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    init = sub.add_parser("init")
    init.add_argument("project")
    init.add_argument("--mode", choices=("create", "recreate", "edit"), required=True)
    init.add_argument("--request-file", required=True)
    init.add_argument("--source", action="append", default=[])
    init.add_argument("--width", type=int, default=1280)
    init.add_argument("--height", type=int, default=720)
    init.add_argument("--fps", default="24")
    for name in ("prepare", "fingerprint", "validate", "pencil-test"):
        command = sub.add_parser(name)
        command.add_argument("project")
        if name != "validate":
            command.add_argument("--shot", required=True)
        if name in {"prepare", "fingerprint", "validate"}:
            command.add_argument("--stage", choices=("rough", "final"), default="final" if name == "validate" else "rough")
        if name in {"prepare", "validate"}:
            command.add_argument("--workers", type=int)
        if name == "validate":
            command.add_argument("--require-complete", action="store_true")
        if name == "pencil-test":
            command.add_argument("--ffmpeg")
            command.add_argument("--ffprobe")
    args = parser.parse_args(argv)
    try:
        if getattr(args, "workers", None) is not None and args.workers < 1:
            raise ProjectError("Worker count must be positive")
        if args.command == "doctor":
            result = doctor()
        elif args.command == "init":
            result = init_project(args.project, args.mode, args.request_file, args.source,
                                  args.width, args.height, args.fps)
        elif args.command == "prepare":
            result = prepare_references(args.project, args.shot, args.stage, args.workers)
        elif args.command == "pencil-test":
            result = pencil_test(args.project, args.shot, args.ffmpeg, args.ffprobe)
        elif args.command == "fingerprint":
            root, data = load_project(args.project)
            result = {"fingerprint": stage_fingerprint(root, data, find_shot(data, args.shot), args.stage),
                      "stage": args.stage, "review_status": "not reviewed by this helper"}
        else:
            result = validate_project(args.project, args.stage, args.require_complete, args.workers)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get("structural_passed") is False else 0
    except (ProjectError, KeyError, TypeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

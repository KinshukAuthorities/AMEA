"""Transport authored 2D contours into editable Grease Pencil; no pose generation.

Run with Blender's Python, or import pure validation/path helpers in normal Python.
See skills/amea/references/blender-2d.md for the scene contract and CLI.
"""
from __future__ import annotations

from array import array
from fractions import Fraction
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import re
import sys
import uuid

TESTED_BLENDER = (5, 2, 2)
TOKEN = re.compile(r"[MLCQZmlcqz]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?")
POINT_LIMIT = 500_000


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def number(value, low=-1e7, high=1e7):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError("Expected a finite number within the supported range")
    return float(value)


def integer(value, low=0):
    if type(value) is not int or value < low:
        raise ValueError("Expected an integer in range")
    return value


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", value):
        raise ValueError("Use a nonempty portable identifier")
    return value


def colour(value, opacity=1):
    """Hex sRGB to linear RGBA; explicit material alpha also covers filled shapes."""
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", value):
        raise ValueError("Colour must be #RRGGBB, #RRGGBBAA or null")
    rgb = [int(value[i:i+2], 16)/255 for i in (1, 3, 5)]
    alpha = int(value[7:9], 16)/255 if len(value) == 9 else 1
    return tuple(c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in rgb) + (alpha*opacity,)


def _mid(a, b):
    return tuple((x+y)/2 for x, y in zip(a, b))


def _distance(p, a, b):
    length = math.dist(a, b)
    return math.dist(p, a) if length < 1e-12 else abs((b[1]-a[1])*p[0]-(b[0]-a[0])*p[1]+b[0]*a[1]-b[1]*a[0])/length


def _cubic(a, b, c, d, out, tolerance, depth=0):
    excess = math.dist(a, b)+math.dist(b, c)+math.dist(c, d)-math.dist(a, d)
    if depth >= 18 or (max(_distance(b, a, d), _distance(c, a, d)) <= tolerance and excess <= tolerance):
        out.append(d)
        if len(out) > POINT_LIMIT:
            raise ValueError("Contour point limit exceeded")
        return
    ab, bc, cd = _mid(a, b), _mid(b, c), _mid(c, d)
    abc, bcd = _mid(ab, bc), _mid(bc, cd)
    centre = _mid(abc, bcd)
    _cubic(a, ab, abc, centre, out, tolerance, depth+1)
    _cubic(centre, bcd, cd, d, out, tolerance, depth+1)


def sample_path(path, tolerance=.25):
    """Sample absolute M/L/C/Q/Z paths, preserving compound subpaths and closure."""
    tolerance = number(tolerance, 1e-4, 2)
    if not isinstance(path, str) or not path.strip():
        raise ValueError("A nonempty authored path is required")
    tokens = TOKEN.findall(path)
    if TOKEN.sub("", path).replace(",", "").strip():
        raise ValueError("Unsupported path syntax")
    i, command, parts, points, closed = 0, None, [], [], False

    def flush():
        nonlocal points, closed
        if points:
            if len(points) > 1 and math.dist(points[0], points[-1]) < 1e-9:
                points.pop()
                closed = True
            if len(points) < (3 if closed else 2):
                raise ValueError("Degenerate subpath")
            parts.append({"points": points, "closed": closed})
        points, closed = [], False

    while i < len(tokens):
        if tokens[i].isalpha():
            command = tokens[i]
            i += 1
        if command not in {"M", "L", "C", "Q", "Z"}:
            raise ValueError("Only absolute M L C Q Z commands are supported")
        if command == "Z":
            if not points:
                raise ValueError("Close command has no subpath")
            closed = True
            flush()
            command = None
            continue
        count = {"M": 2, "L": 2, "C": 6, "Q": 4}[command]
        if i+count > len(tokens) or any(v.isalpha() for v in tokens[i:i+count]):
            raise ValueError("Incomplete path command")
        values = [number(float(x)) for x in tokens[i:i+count]]
        i += count
        if command == "M":
            flush()
            points = [tuple(values)]
            command = "L"
        elif command == "L":
            if not points:
                raise ValueError("Path must begin with M")
            points.append(tuple(values))
        elif command == "C":
            if not points:
                raise ValueError("Curve has no starting point")
            _cubic(points[-1], tuple(values[:2]), tuple(values[2:4]), tuple(values[4:]), points, tolerance)
        else:
            if not points:
                raise ValueError("Curve has no starting point")
            a, q, d = points[-1], tuple(values[:2]), tuple(values[2:])
            b = tuple(x+2/3*(y-x) for x, y in zip(a, q))
            c = tuple(x+2/3*(y-x) for x, y in zip(d, q))
            _cubic(a, b, c, d, points, tolerance)
        if sum(len(p["points"]) for p in parts)+len(points) > POINT_LIMIT:
            raise ValueError("Contour point limit exceeded")
    flush()
    return parts


def width_profile(points, width):
    if isinstance(width, (int, float)) and not isinstance(width, bool):
        return [number(width, 0, 1e5)]*len(points)
    if not isinstance(width, list) or len(width) != 3:
        raise ValueError("Width must be a number or [start, middle, end]")
    start, middle, end = [number(x, 0, 1e5) for x in width]
    lengths = [0.0]
    for a, b in zip(points, points[1:]):
        lengths.append(lengths[-1]+math.dist(a, b))
    total = lengths[-1] or 1
    return [start+(middle-start)*2*t/total if t/total <= .5 else middle+(end-middle)*(2*t/total-1) for t in lengths]


def prepare_drawing(paths):
    """Expand in exact painter order: each path's fill, then its ink, then next path."""
    if not isinstance(paths, list):
        raise ValueError("A drawing is a list of authored paths")
    ids, curves, index = set(), [], []
    ordered = []
    for source_index, path in enumerate(paths):
        if not isinstance(path, dict) or set(path)-{"id", "d", "stroke", "fill", "width", "opacity", "tolerance", "order"}:
            raise ValueError("Unknown authored-path fields")
        path_id = identifier(path["id"])
        if path_id in ids:
            raise ValueError("Duplicate path ID in drawing")
        ids.add(path_id)
        ordered.append((number(path.get("order", source_index)), source_index, path))
    for _, source_index, path in sorted(ordered, key=lambda item: item[:2]):
        parts = sample_path(path["d"], path.get("tolerance", .25))
        opacity = number(path.get("opacity", 1), 0, 1)
        ink, fill = colour(path.get("stroke", "#000000"), opacity), colour(path.get("fill"), opacity)
        widths = [width_profile(p["points"], path.get("width", 2)) for p in parts]
        if fill is not None and any(not p["closed"] for p in parts):
            raise ValueError("A filled contour must be explicitly closed")
        visible_ink = ink is not None and any(max(w) > 0 for w in widths)
        if fill is None and not visible_ink:
            raise ValueError("Path has neither a fill nor visible-width ink")
        for channel, enabled in (("fill", fill is not None), ("ink", visible_ink)):
            if not enabled:
                continue
            offset = len(curves)
            for part, widths_part in zip(parts, widths):
                curves.append({"points": part["points"], "closed": part["closed"],
                               "widths": widths_part if channel == "ink" else [0.0]*len(widths_part),
                               "ink": ink if channel == "ink" else None,
                               "fill": fill if channel == "fill" else None,
                               "fill_id": source_index+1 if channel == "fill" else 0})
            index.append({"curve_start": offset, "curve_count": len(parts), "path_id": path["id"],
                          "source_path_index": source_index, "channel": channel})
    if sum(len(c["points"]) for c in curves) > POINT_LIMIT:
        raise ValueError("Drawing point limit exceeded")
    return {"curves": curves, "index": index}


def validate_scene(spec):
    """Validate and prepare all geometry before any Blender scene mutation."""
    if spec.get("schema_version") != 1:
        raise ValueError("Unsupported scene schema")
    if set(spec)-{"schema_version", "canvas", "frames", "camera", "layers", "background", "audio"}:
        raise ValueError("Unknown scene fields")
    canvas = spec["canvas"]
    if set(canvas) != {"width", "height", "fps"}:
        raise ValueError("Canvas needs width, height and fps")
    integer(canvas["width"], 2)
    integer(canvas["height"], 2)
    rate = Fraction(str(canvas["fps"]))
    if not 0 < rate <= 1000:
        raise ValueError("Invalid frame rate")
    total = integer(spec["frames"], 1)
    background = colour(spec.get("background", "#ffffff"))
    if background is not None and background[3] != 1:
        raise ValueError("World background must be opaque; use null for transparent output")
    if "audio" in spec and (not isinstance(spec["audio"], str) or not spec["audio"].strip()):
        raise ValueError("Audio, when supplied, must name a project-relative mixed sound file")
    cameras = spec["camera"]
    if len(cameras) not in {1, total}:
        raise ValueError("Supply one fixed camera or an explicit camera for every output frame")
    for f, camera in enumerate(cameras):
        if set(camera) != {"frame", "centre", "width"} or camera["frame"] != f or type(camera["frame"]) is not int:
            raise ValueError("Camera samples must be ordered and contiguous from output frame zero")
        if len(camera["centre"]) != 2:
            raise ValueError("Camera centre needs two coordinates")
        for value in camera["centre"]:
            number(value)
        number(camera["width"], 1e-4)
    layers, prepared = spec["layers"], {}
    if not isinstance(layers, list) or not layers:
        raise ValueError("At least one authored layer is required")
    depths = set()
    for layer in layers:
        if set(layer) != {"id", "z", "drawings", "exposures"}:
            raise ValueError("Layer needs id, z, drawings and exposures")
        layer_id = identifier(layer["id"])
        depth = number(layer["z"], -1000, 1000)
        if layer_id in prepared or depth in depths:
            raise ValueError("Layer IDs and depth values must be unique")
        depths.add(depth)
        if not isinstance(layer["drawings"], dict):
            raise ValueError("Drawings must map IDs to path lists")
        prepared[layer_id] = {identifier(key): prepare_drawing(value) for key, value in layer["drawings"].items()}
        cursor = 0
        for exposure in layer["exposures"]:
            if set(exposure) != {"start", "end", "drawing"}:
                raise ValueError("Exposure needs start, end and drawing (or null)")
            start, end = integer(exposure["start"]), integer(exposure["end"], 1)
            if start != cursor or end <= start or end > total:
                raise ValueError("Exposures must tile [0,frames) without gaps or overlap")
            key = exposure["drawing"]
            if key is not None and key not in prepared[layer_id]:
                raise ValueError("Exposure refers to an absent drawing")
            cursor = end
        if cursor != total:
            raise ValueError("Exposure timeline does not cover the output")
    return prepared


def require_api(allow_unverified_version=False):
    import bpy
    if tuple(bpy.app.version[:3]) != TESTED_BLENDER and not allow_unverified_version:
        raise RuntimeError("This backend was calibrated on Blender 5.2.2; test another version explicitly with --allow-unverified-version")
    if not hasattr(bpy.data, "grease_pencils") or not hasattr(bpy.data.materials, "create_gpencil_data"):
        raise RuntimeError("Required modern Grease Pencil API is unavailable")


def preflight_backend(spec, base):
    """Check actual RNA bounds and open the audio reader before changing scene data."""
    import bpy

    def within(properties, name, value):
        prop = properties[name]
        if not prop.hard_min <= value <= prop.hard_max:
            raise ValueError(f"{name} exceeds the selected Blender backend's hard limits")

    render_properties = bpy.types.RenderSettings.bl_rna.properties
    within(render_properties, "resolution_x", spec["canvas"]["width"])
    within(render_properties, "resolution_y", spec["canvas"]["height"])
    rate = Fraction(str(spec["canvas"]["fps"]))
    fps = max(1, round(float(rate)))
    within(render_properties, "fps", fps)
    within(render_properties, "fps_base", fps/float(rate))
    within(bpy.types.Scene.bl_rna.properties, "frame_end", spec["frames"])
    within(bpy.types.GreasePencilFrame.bl_rna.properties, "frame_number", spec["frames"]+1)
    for camera in spec["camera"]:
        within(bpy.types.Camera.bl_rna.properties, "ortho_scale", camera["width"])
    audio, audio_info = None, None
    if "audio" in spec:
        if Path(spec["audio"]).is_absolute():
            raise ValueError("Audio must be a project-relative file")
        audio = (base/spec["audio"]).resolve()
        if not audio.is_relative_to(base) or not audio.is_file():
            raise ValueError("Audio must exist inside the source project")
        try:
            import aud
            reader = aud.Sound(str(audio))
            sample_rate, channels = reader.specs
            samples = reader.length
            if not all(math.isfinite(v) and v > 0 for v in (sample_rate, channels, samples)):
                raise ValueError("Invalid sound stream metadata")
        except Exception as error:
            raise ValueError("Mixed sound must have a readable, nonempty audio stream") from error
        seconds = samples/sample_rate
        if abs(seconds-float(spec["frames"]/rate)) > max(.03, 1/float(rate)):
            raise ValueError("Prepare mixed audio aligned to the full output duration")
        audio_info = {"sample_rate": sample_rate, "channels": channels, "sample_frames": samples,
                      "seconds": seconds, "reader_validated": True, "listening": "pending"}
    return audio, audio_info


def new_object(name, z=0):
    import bpy
    data = bpy.data.grease_pencils.new(name)
    data.stroke_depth_order = "2D"
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location.z = z
    return obj


def write_drawing(obj, layer, native_frame, prepared, materials):
    """One bulk attribute transfer per attribute, with independently editable curves."""
    import bpy
    drawing = layer.frames.new(native_frame).drawing
    curves = prepared["curves"]
    if not curves:
        return
    drawing.add_strokes([len(c["points"]) for c in curves])
    positions, radii = array("f"), array("f")
    cyclic, material_indices, fill_ids, hide = [], [], [], []
    for curve in curves:
        key = (curve["ink"], curve["fill"])
        if key not in materials:
            material = bpy.data.materials.new("AMEA contour material")
            bpy.data.materials.create_gpencil_data(material)
            style = material.grease_pencil
            style.show_stroke = curve["ink"] is not None
            style.show_fill = curve["fill"] is not None
            style.color = curve["ink"] or (0, 0, 0, 0)
            style.fill_color = curve["fill"] or (0, 0, 0, 0)
            obj.data.materials.append(material)
            materials[key] = len(obj.data.materials)-1
        for (x, y), width in zip(curve["points"], curve["widths"]):
            positions.extend((x, y, 0))
            radii.append(width/2)
        cyclic.append(curve["closed"])
        material_indices.append(materials[key])
        fill_ids.append(curve["fill_id"])
        hide.append(curve["ink"] is None)
    drawing.attributes["position"].data.foreach_set("vector", positions)
    for name, data_type, domain, values in (
        ("radius", "FLOAT", "POINT", radii),
        ("opacity", "FLOAT", "POINT", [1.0]*len(radii)),
        ("cyclic", "BOOLEAN", "CURVE", cyclic),
        ("material_index", "INT", "CURVE", material_indices),
        ("fill_id", "INT", "CURVE", fill_ids),
        ("hide_stroke", "BOOLEAN", "CURVE", hide),
    ):
        attr = drawing.attributes.get(name) or drawing.attributes.new(name, data_type, domain)
        attr.data.foreach_set("value", values)
    drawing.tag_positions_changed()


def build_scene(spec, base, allow_unverified_version=False):
    """Create a fresh scene only after validation. Call in a separate Blender process."""
    import bpy
    prepared = validate_scene(spec)
    require_api(allow_unverified_version)
    base = Path(base).resolve()
    audio, audio_info = preflight_backend(spec, base)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "AMEA drawn animation"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = spec["canvas"]["width"]
    scene.render.resolution_y = spec["canvas"]["height"]
    scene.render.resolution_percentage = 100
    rate = Fraction(str(spec["canvas"]["fps"]))
    scene.render.fps = max(1, round(float(rate)))
    scene.render.fps_base = scene.render.fps/float(rate)
    scene.frame_start, scene.frame_end = 1, spec["frames"]
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = "background" in spec and spec["background"] is None
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.world = bpy.data.worlds.new("AMEA background")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = colour(spec.get("background", "#ffffff")) or (0, 0, 0, 0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1
    camera = bpy.data.objects.new("AMEA camera", bpy.data.cameras.new("AMEA orthographic camera"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = "ORTHO"
    camera.data.sensor_fit = "HORIZONTAL"
    camera.data.clip_end = 10000
    for key in spec["camera"]:
        camera.location = (*key["centre"], 2000)
        camera.data.ortho_scale = key["width"]
        if len(spec["camera"]) > 1:
            camera.keyframe_insert("location", frame=key["frame"]+1)
            camera.data.keyframe_insert("ortho_scale", frame=key["frame"]+1)
    index, layers_report = {}, []
    for source in spec["layers"]:
        name = source["id"]
        obj = new_object(name, source["z"])
        layer = obj.data.layers.new("Authored fill and ink", set_active=True)
        layer.use_lights = False
        previous, materials, events = object(), {}, []
        index[name] = {}
        for exposure in source["exposures"]:
            key = exposure["drawing"]
            drawing = prepared[name][key] if key is not None else {"curves": [], "index": []}
            signature = digest(drawing)
            if signature == previous:
                continue
            frame = exposure["start"]+1
            write_drawing(obj, layer, frame, drawing, materials)
            index[name][str(frame)] = {"drawing_id": key, "source_sha256": digest(source["drawings"][key]) if key is not None else None,
                                      "curves": drawing["index"]}
            previous = signature
            events.append(frame)
        layer.frames.new(spec["frames"]+1)
        obj["source_layer"] = name
        obj["curve_index"] = "AMEA_CURVE_INDEX.json"
        layers_report.append({"id": name, "native_keys": events+[spec["frames"]+1], "materials": len(materials)})
    if audio:
        strip = scene.sequence_editor_create().strips.new_sound("AMEA mixed audio", str(audio), channel=1, frame_start=1)
        strip.sound.pack()
        scene.render.use_sequencer = False
    for name, value in (("AMEA_SOURCE.json", spec), ("AMEA_CURVE_INDEX.json", index)):
        bpy.data.texts.new(name).write(json.dumps(value, indent=1, allow_nan=False))
    scene["coordinate_contract"] = "Authored XY; origin centred; +x right,+y up; output f maps to native f+1. Projection occurs before transport."
    scene.frame_set(1)
    return {"schema_version": 1, "source_sha256": digest(spec), "blender_version": bpy.app.version_string,
            "backend_version_calibrated": tuple(bpy.app.version[:3]) == TESTED_BLENDER,
            "frames": spec["frames"], "layers": layers_report, "audio_packed": bool(audio), "audio": audio_info,
            "review": "Native transport only; construction, motion, playback and sound review remain pending."}


def compile_file(source, output, allow_unverified_version=False):
    import bpy
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.suffix.lower() != ".blend" or output.exists():
        raise ValueError("Choose a new .blend output; existing native work is preserved")
    report_path = output.with_suffix(".transport.json")
    if report_path.exists():
        raise FileExistsError(report_path)
    spec = json.loads(source.read_text(encoding="utf-8-sig"))
    report = build_scene(spec, source.parent, allow_unverified_version)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.stem+"."+uuid.uuid4().hex+".tmp.blend")
    try:
        bpy.ops.wm.save_as_mainfile(filepath=str(temporary), check_existing=False)
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    report["native_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
    report["backend_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-unverified-version", action="store_true", help="Calibration only; report stays version-unverified")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    print(json.dumps(compile_file(args.source, args.output, args.allow_unverified_version), indent=2))


if __name__ == "__main__":
    main()

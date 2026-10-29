"""Contoured native transport checks; synthetic geometry is not anime-quality evidence."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"tools"))
import blender_2d as gp
import common


def fixture():
    a = [
        {"id": "base", "d": "M -26 -18 L 24 -18 L 24 18 L -26 18 Z", "fill": "#c85842", "stroke": "#222d35", "width": [1, 3, 1]},
        {"id": "overlap", "d": "M -8 -8 Q 0 26 21 7 L 21 -8 Z", "fill": "#76a37a", "stroke": "#173a33", "width": 2},
        {"id": "ink", "d": "M -30 1 C -20 24 8 -20 28 13", "fill": None, "stroke": "#292c42", "width": [1, 4, 1]},
    ]
    b = copy.deepcopy(a)
    b[1]["d"] = "M -15 -8 Q 4 16 25 12 L 25 -8 Z"
    return {"schema_version": 1, "canvas": {"width": 96, "height": 72, "fps": "24"},
            "frames": 8, "background": None, "camera": [{"frame": 0, "centre": [0, 0], "width": 96}],
            "layers": [{"id": "contours", "z": 0, "drawings": {"a": a, "b": b},
                        "exposures": [{"start": 0, "end": 2, "drawing": "a"}, {"start": 2, "end": 4, "drawing": "b"},
                                      {"start": 4, "end": 6, "drawing": "a"}, {"start": 6, "end": 8, "drawing": None}]}]}


class PathAndSceneTests(unittest.TestCase):
    def test_curves_and_compound_closure(self):
        parts = gp.sample_path("M 0 0 C 0 20 20 20 20 0 L 0 0 Z M 4 2 Q 7 12 10 2 Z")
        self.assertEqual(len(parts), 2)
        self.assertTrue(all(p["closed"] for p in parts))
        self.assertGreater(len(parts[0]["points"]), 4)
        self.assertEqual(parts[0]["points"][0], (0, 0))
        for invalid in ["M 0 0 l 1 1", "M 0 0 C 4", "M 0 0 A 4 5 0 0 0 9 9", "M 0 0 Z", "M 0 0 L 1e99 0"]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                gp.sample_path(invalid)

    def test_painter_channels_and_fill_alpha(self):
        paths = fixture()["layers"][0]["drawings"]["a"]
        paths[1]["opacity"] = .25
        prepared = gp.prepare_drawing(paths)
        self.assertEqual([(i["path_id"], i["channel"]) for i in prepared["index"]],
                         [("base", "fill"), ("base", "ink"), ("overlap", "fill"), ("overlap", "ink"), ("ink", "ink")])
        self.assertEqual(prepared["curves"][2]["fill"][3], .25)
        self.assertEqual(prepared["curves"][3]["ink"][3], .25)
        self.assertIsNone(prepared["curves"][0]["ink"])
        self.assertEqual(gp.colour("#ffffff80", .5)[3], 128/255*.5)

    def test_invalid_inputs_and_explicit_exposure_coverage(self):
        spec = fixture()
        self.assertEqual(set(gp.validate_scene(spec)), {"contours"})
        mutations = [
            lambda s: s["layers"][0]["exposures"][1].update(start=3),
            lambda s: s["layers"][0]["exposures"][1].update(drawing="missing"),
            lambda s: s["layers"].append(copy.deepcopy(s["layers"][0])),
            lambda s: s["layers"][0]["drawings"]["a"][0].update(d="M 0 0 L 10 0"),
            lambda s: s["layers"][0]["drawings"]["a"][0].update(opacity=2),
            lambda s: s["layers"][0]["drawings"]["a"][1].update(id="base"),
            lambda s: s["layers"][0]["drawings"]["a"][0].update(unknown=1),
            lambda s: s.update(frames=True),
            lambda s: s["camera"][0].update(width=float("nan")),
            lambda s: s["canvas"].update(fps="0"),
            lambda s: s.update(audio=False),
            lambda s: s.update(background="#ffffff80"),
        ]
        for mutation in mutations:
            candidate = copy.deepcopy(spec)
            mutation(candidate)
            with self.assertRaises((ValueError, ZeroDivisionError)):
                gp.validate_scene(candidate)


class NativeTransportTests(unittest.TestCase):
    @unittest.skipUnless(common.discover("blender"), "Optional Blender executable unavailable")
    def test_compile_reopen_paint_order_alpha_and_exposures(self):
        blender = common.discover("blender")
        work = ROOT/"tests/.work"
        work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as directory:
            base = Path(directory)
            spec = fixture()
            with wave.open(str(base/"mixed.wav"), "wb") as sound:
                sound.setnchannels(2)
                sound.setsampwidth(2)
                sound.setframerate(48000)
                sound.writeframes(b'\0'*(16000*2*2))
            spec["audio"] = "mixed.wav"
            source, native = base/"scene.json", base/"film.blend"
            source.write_text(json.dumps(spec), encoding="utf-8")
            command = [blender, "-b", "--python-exit-code", "1", "--python", str(ROOT/"tools/blender_2d.py"), "--", str(source), "--output", str(native)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout[-2000:]+result.stderr[-2000:])
            before = common.sha256(native)
            report = json.loads(native.with_suffix(".transport.json").read_text())
            self.assertEqual(report["native_sha256"], before)
            self.assertEqual(report["layers"][0]["native_keys"], [1, 3, 5, 7, 9])
            self.assertTrue(report["audio_packed"])
            self.assertTrue(report["audio"]["reader_validated"])
            # Existing work is rejected without overwriting it.
            again = subprocess.run(command, capture_output=True, text=True, timeout=90)
            self.assertNotEqual(again.returncode, 0)
            self.assertEqual(common.sha256(native), before)
            probe = base/"probe.py"
            probe.write_text('''import bpy,json,sys,copy
from pathlib import Path
sys.path.insert(0, TOOL_DIR)
import blender_2d as gp
base=Path(BASE)
scene=bpy.context.scene
scene.render.threads_mode='FIXED';scene.render.threads=2
obj=bpy.data.objects['contours'];layer=obj.data.layers[0]
assert [f.frame_number for f in layer.frames]==[1,3,5,7,9]
assert len(layer.frames[0].drawing.strokes)==5
assert len(layer.frames[-1].drawing.strokes)==0
assert len(json.loads(bpy.data.texts['AMEA_CURVE_INDEX.json'].as_string())['contours']['1']['curves'])==5
assert not [o for o in scene.objects if o.type=='MESH']
assert len(bpy.data.sounds)==1 and bpy.data.sounds[0].packed_file
def render(name,frame):
    scene.frame_set(frame);scene.render.filepath=str(base/name)
    bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(base/name),check_existing=False)
    values=tuple(im.pixels[:]);bpy.data.images.remove(im);return values
a=render('a.png',1);hold=render('hold.png',2);b=render('b.png',3)
assert a==hold and a!=b
assert a==render('repeat.png',5)
assert not any(render('blank.png',7)[3::4])
# Independent transport reference: one native layer per authored path.
obj.hide_render=True
reference=gp.new_object('reference')
for i,path in enumerate(json.loads((base/'scene.json').read_text())['layers'][0]['drawings']['a']):
    ref_layer=reference.data.layers.new(str(i),set_active=True);ref_layer.use_lights=False
    gp.write_drawing(reference,ref_layer,1,gp.prepare_drawing([path]),{})
assert a==render('reference.png',1), 'Bulk painter order differs from per-path reference'
reference.hide_render=True
# Explicit alpha belongs to fill material, not only point opacity.
alpha=gp.new_object('alpha')
alpha_layer=alpha.data.layers.new('alpha',set_active=True);alpha_layer.use_lights=False
gp.write_drawing(alpha,alpha_layer,1,gp.prepare_drawing([{'id':'alpha','d':'M -10 -10 L 10 -10 L 10 10 L -10 10 Z','stroke':None,'fill':'#50a060','opacity':.25}]),{})
values=render('alpha.png',1);centre=(36*96+48)*4
assert .23<values[centre+3]<.27,values[centre:centre+4]
# Invalid settings must fail before replacing the current native scene.
spec=json.loads((base/'scene.json').read_text())
(base/'invalid.wav').write_text('Not an audio stream')
cases=[]
for width in [2,70000]:
    bad=copy.deepcopy(spec);bad['canvas']['width']=width;cases.append(bad)
bad=copy.deepcopy(spec);bad['frames']=2000000;bad['layers'][0]['exposures']=[{'start':0,'end':2000000,'drawing':'a'}];cases.append(bad)
bad=copy.deepcopy(spec);bad['canvas']['fps']='1/1000000000';cases.append(bad)
for audio in [False,'invalid.wav']:
    bad=copy.deepcopy(spec);bad['audio']=audio;cases.append(bad)
sentinel=(bpy.context.scene.as_pointer(),sorted(o.name for o in bpy.data.objects),len(bpy.data.sounds))
for bad in cases:
    try:gp.build_scene(bad,base)
    except ValueError:pass
    else:raise AssertionError('Invalid backend input was accepted')
    assert sentinel==(bpy.context.scene.as_pointer(),sorted(o.name for o in bpy.data.objects),len(bpy.data.sounds))
(base/'probe.json').write_text(json.dumps({'fresh_reopen':True,'painter_pixels_identical':True,'holds_identical':True,'different_poses':True,'fill_alpha':values[centre+3]}))
'''.replace("TOOL_DIR", repr(str(ROOT/"tools"))).replace("BASE", repr(str(base))), encoding="utf-8")
            result = subprocess.run([blender, "-b", str(native), "--python-exit-code", "1", "--python", str(probe)], capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout[-3000:]+result.stderr[-3000:])
            self.assertTrue(json.loads((base/"probe.json").read_text())["painter_pixels_identical"])


if __name__ == "__main__":
    unittest.main()

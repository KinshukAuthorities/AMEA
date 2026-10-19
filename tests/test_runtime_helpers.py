"""Behavior checks for safe cache resuming, frame integrity, audits and asset handoffs."""
import importlib.util,json,os,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];TOOLS=ROOT/'tools';WORK=ROOT/'tests/.work';WORK.mkdir(exist_ok=True)
sys.path.insert(0,str(TOOLS))
import common,render_queue,asset_handoff

class PathAndHandoffTests(unittest.TestCase):
    def test_handoff_preserves_inputs_and_requires_actual_files(self):
        from PIL import Image
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            root=Path(tmp);brief=root/'brief.txt';brief.write_text('Synthetic asset brief.')
            image=root/'input.png';Image.new('RGBA',(4,4),(8,16,32,128)).save(image)
            before=common.sha256(image);result=asset_handoff.prepare(root/'handoff',brief,[image])
            manifest=json.loads((root/'handoff/asset-handoff.json').read_text())
            self.assertEqual(manifest['references'][0]['sha256'],before);self.assertEqual(common.sha256(image),before)
            with zipfile.ZipFile(result['archive']) as z:
                self.assertIn('references/reference-01.png',z.namelist());self.assertIsNone(z.testzip())
            with self.assertRaises(FileExistsError):asset_handoff.prepare(root/'handoff',brief,[image])
            with self.assertRaises(FileNotFoundError):asset_handoff.prepare(root/'missing-handoff',brief,[root/'missing.png'])
            self.assertFalse((root/'missing-handoff').exists())

    def test_output_cannot_escape_project(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            with self.assertRaises(ValueError):common.project_output(tmp,'../outside')
            with self.assertRaises(ValueError):common.project_output(tmp,'.')
            self.assertTrue(common.project_output(tmp,'renders/current').is_relative_to(Path(tmp)))

class BlenderIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(common.discover('blender') and common.discover('ffmpeg') and common.discover('ffprobe'),'Optional Blender and FFmpeg integration tools unavailable')
    def test_disjoint_render_resume_corrupt_frame_and_contact_audit(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            root=Path(tmp).resolve();scene=root/'scene.blend';creator=root/'create.py'
            creator.write_text('''import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
bpy.ops.mesh.primitive_cube_add();cube=bpy.context.object
cube.location.x=0;cube.keyframe_insert('location',frame=0)
cube.location.x=.25;cube.keyframe_insert('location',frame=3)
bpy.ops.object.camera_add(location=(4,-6,3));camera=bpy.context.object
camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH';scene.frame_start=0;scene.frame_end=3
bpy.ops.object.empty_add(location=(.25,0,0));bpy.context.object.name='ContactTarget'
bpy.ops.object.empty_add(location=(0,0,0));bpy.context.object.name='ContactPoint'
bpy.ops.object.armature_add();bpy.context.object.name='TestRig'
bpy.ops.wm.save_as_mainfile(filepath='''+repr(str(scene))+''')
''',encoding='utf-8')
            blender=common.discover('blender')
            r=subprocess.run([blender,'-b','--python',str(creator)],capture_output=True,text=True,timeout=120)
            self.assertEqual(r.returncode,0,r.stderr[-2000:]);self.assertTrue(scene.is_file())
            job={'scene':'scene.blend','start':0,'end':3,'fps':'24','width':64,'height':48,'output_dir':'renders','review_frames':[0,3]}
            jobfile=root/'job.json';common.write_json(jobfile,job)
            result=render_queue.render(jobfile,blender,workers=2,threads=1)
            folder=Path(result['generation']);frames=sorted((folder/'frames').glob('frame_*.png'))
            self.assertEqual(result['delivery']['decoded_frames'],4);self.assertEqual(len(frames),4)
            self.assertEqual(result['delivery']['visual_review'],'pending');self.assertIsNone(result['delivery']['audio_seconds'])
            self.assertEqual(len(list(folder.glob('encoded-review-*.png'))),2)
            times={p.name:p.stat().st_mtime_ns for p in frames}
            again=render_queue.render(jobfile,blender,workers=1,threads=1)
            self.assertEqual(result['generation'],again['generation'])
            self.assertEqual(times,{p.name:p.stat().st_mtime_ns for p in frames})
            frames[1].write_bytes(b'corrupt')
            render_queue.render(jobfile,blender,workers=1,threads=1)
            self.assertTrue(render_queue.frame_valid(frames[1],(64,48)))
            for p in [frames[0],*frames[2:]]:self.assertEqual(p.stat().st_mtime_ns,times[p.name])
            job.update(width=66,end=0,review_frames=[],encode=False);common.write_json(jobfile,job)
            different=render_queue.render(jobfile,blender,workers=1,threads=1)
            self.assertNotEqual(result['generation'],different['generation']);self.assertTrue((folder/'animation.mp4').is_file())
            contacts=root/'contacts.json';report=root/'audit.json'
            common.write_json(contacts,[{'frame':0,'object':'ContactPoint','target_object':'ContactTarget','tolerance':.1}])
            r=subprocess.run([blender,'-b',str(scene),'--python',str(TOOLS/'blender_audit.py'),'--','--output',str(report),'--contacts',str(contacts)],capture_output=True,text=True,timeout=120)
            self.assertEqual(r.returncode,0,r.stderr[-2000:]);audit=json.loads(report.read_text())
            self.assertAlmostEqual(audit['contacts'][0]['distance_units'],.25)
            self.assertFalse(audit['contacts'][0]['within_declared_tolerance']);self.assertIn('TestRig',audit['rigs'])

if __name__=='__main__':unittest.main()

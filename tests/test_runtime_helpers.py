"""Behavior checks for safe cache resuming, frame integrity, drawn animation rendering."""
import importlib.util,json,os,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];TOOLS=ROOT/'tools';WORK=ROOT/'tests/.work';WORK.mkdir(exist_ok=True)
sys.path.insert(0,str(TOOLS))
import common,render_queue

class PathTests(unittest.TestCase):
    def test_output_cannot_escape_project(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            with self.assertRaises(ValueError):common.project_output(tmp,'../outside')
            with self.assertRaises(ValueError):common.project_output(tmp,'.')
            self.assertTrue(common.project_output(tmp,'renders/current').is_relative_to(Path(tmp)))

class BlenderIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(common.discover('blender') and common.discover('ffmpeg') and common.discover('ffprobe'),'Optional Blender and FFmpeg integration tools unavailable')
    def test_disjoint_render_resume_corrupt_frame(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            root=Path(tmp).resolve();scene=root/'scene.blend';creator=root/'create.py'
            creator.write_text('''import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
bpy.ops.object.grease_pencil_add(type='STROKE');cube=bpy.context.object
cube.location.x=0;cube.keyframe_insert('location',frame=0)
cube.location.x=.25;cube.keyframe_insert('location',frame=3)
bpy.ops.object.camera_add(location=(4,-6,3));camera=bpy.context.object
camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
scene.render.engine='BLENDER_WORKBENCH';scene.frame_start=0;scene.frame_end=3
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
            self.assertTrue(result['delivery']['full_decode_passed'])
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
            # A valid but edited same-size PNG is also stale, even though it decodes.
            from PIL import Image
            Image.new('RGB',(64,48),(255,0,200)).save(frames[1])
            self.assertTrue(render_queue.frame_valid(frames[1],(64,48)))
            self.assertFalse(render_queue.cached_frame_valid(frames[1],(64,48)))
            render_queue.render(jobfile,blender,workers=1,threads=1)
            self.assertTrue(render_queue.cached_frame_valid(frames[1],(64,48)))
            for p in [frames[0],*frames[2:]]:self.assertEqual(p.stat().st_mtime_ns,times[p.name])
            job.update(width=66,end=0,review_frames=[],encode=False);common.write_json(jobfile,job)
            different=render_queue.render(jobfile,blender,workers=1,threads=1)
            self.assertNotEqual(result['generation'],different['generation']);self.assertTrue((folder/'animation.mp4').is_file())

if __name__=='__main__':unittest.main()

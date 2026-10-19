"""One disjoint frame range; run through the selected Blender executable."""
import argparse,json,os,sys
from pathlib import Path
import bpy

def valid_frame(path,size):
    if not path.is_file():return False
    image=None
    try:
        image=bpy.data.images.load(str(path),check_existing=False)
        return tuple(image.size)==tuple(size)
    except Exception:return False
    finally:
        if image is not None:bpy.data.images.remove(image)

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--first',type=int,required=True);p.add_argument('--last',type=int,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run=json.loads(a.run.read_text(encoding='utf-8'))
    job=run['job'];out=a.run.parent/'frames';out.mkdir(exist_ok=True);scene=bpy.context.scene
    scene.render.resolution_x=job['width'];scene.render.resolution_y=job['height'];scene.render.resolution_percentage=100
    from fractions import Fraction
    fps=Fraction(str(job['fps']));scene.render.fps=max(1,round(float(fps)));scene.render.fps_base=scene.render.fps/float(fps)
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.compression=20
    scene.render.threads_mode='FIXED';scene.render.threads=run['threads']
    if 'samples' in job:
        if hasattr(scene,'eevee') and hasattr(scene.eevee,'taa_render_samples'):scene.eevee.taa_render_samples=job['samples']
        if scene.render.engine=='CYCLES':scene.cycles.samples=job['samples']
    for f in range(a.first,a.last+1):
        path=out/f'frame_{f:06d}.png'
        if valid_frame(path,[job['width'],job['height']]):continue
        scene.frame_set(f);temp=out/f'.frame_{f:06d}-{os.getpid()}.png';scene.render.filepath=str(temp)
        bpy.ops.render.render(write_still=True)
        if not valid_frame(temp,[job['width'],job['height']]):raise RuntimeError(f'Invalid rendered frame {f}')
        os.replace(temp,path);print('AMEA_FRAME_COMPLETE',f,flush=True)

if __name__=='__main__':main()

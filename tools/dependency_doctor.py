"""Inventory dependencies without installing packages, downloading models, or choosing software."""
import argparse,importlib.metadata as metadata,importlib.util,json,os,platform,shutil,sys
from pathlib import Path
from common import discover

def inspect(profile='drawing',deep=False):
    names=['Pillow']
    if profile=='trellis':names+=['torch','torchvision','numpy','imageio','opencv-python-headless','tqdm','trimesh','safetensors']
    versions={};missing=[]
    for name in dict.fromkeys(names):
        try:versions[name]=metadata.version(name)
        except metadata.PackageNotFoundError:missing.append(name)
    report={'python':sys.executable,'python_version':platform.python_version(),'platform':platform.platform(),
        'profile':profile,'versions':versions,'missing_packages':missing,'logical_cpus':os.cpu_count(),
        'free_bytes':shutil.disk_usage(Path.cwd()).free,
        'available_optional_tools':{n:discover(n) for n in ['blender','krita','ffmpeg','ffprobe']},
        'preferences':'Reuse established choices; ask for missing 2D/3D and software preferences before production.',
        'gui_control':'Not tested','image_generation':'Verify host capability; not supplied by pip',
        'speech_generation':'Not configured; not mandatory','artistic_quality':'Not tested','smoke_checks':{}}
    if profile=='trellis':report['backend_runtime']='Native extensions, source imports and real generation still require testing in the selected TRELLIS.2 environment.'
    if deep:
        if 'Pillow' in versions:
            try:
                from PIL import Image
                im=Image.new('RGBA',(2,2),(1,2,3,128));report['smoke_checks']['pillow']=im.getpixel((0,0))==(1,2,3,128)
            except Exception as e:report['smoke_checks']['pillow_error']=str(e)
        if profile=='trellis' and 'torch' in versions:
            try:
                import torch
                device='cuda' if torch.cuda.is_available() else 'cpu'
                report['smoke_checks']['tensor']={'device':device,'sum':torch.arange(6,device=device).sum().item(),
                    'torch':torch.__version__,
                    'gpu':torch.cuda.get_device_name(0) if device=='cuda' else None}
            except Exception as e:report['smoke_checks']['tensor_error']=str(e)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',choices=['drawing','trellis'],default='drawing');p.add_argument('--deep',action='store_true')
    a=p.parse_args();print(json.dumps(inspect(a.profile,a.deep),indent=2))

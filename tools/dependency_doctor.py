"""Inventory dependencies without installing packages, downloading models, or choosing software."""
import argparse,importlib.metadata as metadata,importlib.util,json,os,platform,shutil,sys
from pathlib import Path
from common import discover

def inspect(profile='drawing',deep=False):
    names=['Pillow']
    versions={};missing=[]
    for name in dict.fromkeys(names):
        try:versions[name]=metadata.version(name)
        except metadata.PackageNotFoundError:missing.append(name)
    report={'python':sys.executable,'python_version':platform.python_version(),'platform':platform.platform(),
        'profile':profile,'versions':versions,'missing_packages':missing,'logical_cpus':os.cpu_count(),
        'free_bytes':shutil.disk_usage(Path.cwd()).free,
        'available_optional_tools':{n:discover(n) for n in ['blender','krita','ffmpeg','ffprobe']},
        'preferences':'Use canonical workflow-selection.md: explicit/inherited choices first; otherwise authored drawn 2D in Blender. Ask only genuinely unresolved choices.',
        'gui_control':'Not tested','image_generation':'Optional for a selected generation task; not needed by default authored 2D and not supplied by pip',
        'speech_generation':'Not configured; not mandatory','artistic_quality':'Not tested','smoke_checks':{}}
    if deep:
        if 'Pillow' in versions:
            try:
                from PIL import Image
                im=Image.new('RGBA',(2,2),(1,2,3,128));report['smoke_checks']['pillow']=im.getpixel((0,0))==(1,2,3,128)
            except Exception as e:report['smoke_checks']['pillow_error']=str(e)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',choices=['drawing'],default='drawing');p.add_argument('--deep',action='store_true')
    a=p.parse_args();print(json.dumps(inspect(a.profile,a.deep),indent=2))

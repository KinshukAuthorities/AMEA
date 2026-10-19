"""Small, dependency-free tool/path helpers; no installation or network actions."""
import hashlib,json,os,shutil,tempfile
from pathlib import Path

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while block:=f.read(4*1024*1024):h.update(block)
    return h.hexdigest()

def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=path.parent,delete=False,suffix='.tmp') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n');temp=Path(f.name)
    try:os.replace(temp,path)
    finally:temp.unlink(missing_ok=True)

def discover(name,explicit=None):
    if explicit:
        p=Path(explicit).expanduser().resolve()
        if not p.is_file():raise FileNotFoundError(p)
        return str(p)
    configured=os.environ.get('AMEA_'+name.upper())
    if configured and Path(configured).is_file():return str(Path(configured).resolve())
    found=shutil.which(name)
    if found:return found
    candidates=[]
    if os.name=='nt':
        pf=Path(os.environ.get('ProgramFiles',r'C:\Program Files'))
        if name=='blender':candidates=sorted((pf/'Blender Foundation').glob('Blender */blender.exe'),reverse=True)
        if name=='krita':candidates=[pf/'Krita (x64)/bin/krita.exe',pf/'Krita/bin/krita.exe']
        if name in {'ffmpeg','ffprobe'}:
            folder=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData/Local')))/'Microsoft/WinGet/Packages'
            candidates=sorted(folder.glob(f'Gyan.FFmpeg*/*/bin/{name}.exe'),reverse=True)
    return next((str(p) for p in candidates if p.is_file()),None)

def project_output(base,value):
    base=Path(base).resolve();p=(base/value).resolve()
    if p==base or not p.is_relative_to(base):raise ValueError('Output must be inside the project directory')
    return p

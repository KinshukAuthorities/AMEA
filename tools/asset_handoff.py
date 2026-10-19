"""Prepare reference images and export directions for user-operated 3D generation."""
import argparse,json,shutil,zipfile
from pathlib import Path
from common import sha256,write_json

DEFAULT_URL='https://huggingface.co/spaces/microsoft/TRELLIS.2'

def prepare(output,brief,images,provider_url=DEFAULT_URL):
    output=Path(output).resolve();brief=Path(brief).resolve();images=[Path(p).resolve() for p in images]
    if output.exists():raise FileExistsError('Choose a new handoff folder; existing work will not be overwritten')
    if not images:raise ValueError('At least one actual reference image is required')
    for file in [brief,*images]:
        if not file.is_file() or not file.stat().st_size:raise FileNotFoundError(file)
    output.mkdir(parents=True);refs=output/'references';refs.mkdir()
    shutil.copy2(brief,output/'asset-brief.txt');records=[]
    for i,file in enumerate(images,1):
        name=f'reference-{i:02d}'+file.suffix.lower();dest=refs/name;shutil.copy2(file,dest)
        records.append({'path':dest.relative_to(output).as_posix(),'original_name':file.name,'sha256':sha256(dest),
                        'role':'primary conditioning reference' if i==1 else 'supplementary design/review reference'})
    manifest={'provider_url':provider_url,'brief':'asset-brief.txt','references':records,
        'expected_return':'Generated GLB plus any external textures/material files; retain the generated design.',
        'stage':'Prepared references only; generation, import, rigging, deformation and artistic review are pending.'}
    write_json(output/'asset-handoff.json',manifest)
    (output/'RETURN-INSTRUCTIONS.md').write_text(
        '# Asset generation handoff\n\n'
        f'Open [the selected generator]({provider_url}). Read `asset-brief.txt`.\n\n'
        '1. Upload the primary image in `references/`. Use supplementary views as input only if the selected service supports them.\n'
        '2. Generate and inspect the asset from the needed views against the supplied references.\n'
        '3. Use the service\'s GLB export. In the official TRELLIS.2 demo this is **Extract GLB**.\n'
        '4. Return the downloaded `.glb` and any companion texture/material files to the agent.\n\n'
        'The agent will inspect, import, correct, rig and animate the asset as required. A preview screenshot is not a replacement for the exported geometry.\n',encoding='utf-8')
    files=sorted(p for p in output.rglob('*') if p.is_file());archive=output/'asset-handoff.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for file in files:z.write(file,file.relative_to(output).as_posix())
    return {'folder':str(output),'archive':str(archive),'references':len(records),'stage':'handoff prepared'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--brief',type=Path,required=True);p.add_argument('--images',type=Path,nargs='+',required=True);p.add_argument('--provider-url',default=DEFAULT_URL);a=p.parse_args()
    print(json.dumps(prepare(a.output,a.brief,a.images,a.provider_url),indent=2))

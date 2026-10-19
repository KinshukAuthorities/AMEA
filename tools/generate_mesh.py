"""Generate original unrigged geometry from an image using explicitly supplied local tools."""
import argparse,gc,hashlib,json,os,sys,time
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--image',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--seed',type=int,default=0);p.add_argument('--steps',type=int,default=32)
    p.add_argument('--resolution',type=int,default=512);p.add_argument('--chunks',type=int,default=8192)
    p.add_argument('--threads',type=int,default=4);p.add_argument('--device',choices=['auto','cuda','cpu'],default='auto')
    p.add_argument('--largest-component',action='store_true');p.add_argument('--allow-opaque',action='store_true')
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('Use a new output revision; existing mesh will not be overwritten')
    if min(a.steps,a.resolution,a.chunks,a.threads)<=0:raise ValueError('Settings must be positive')
    for file in [a.image,a.checkpoint/'config.yaml',a.checkpoint/'model.fp16.safetensors']:
        if not file.is_file():raise FileNotFoundError(file)
    if not (a.source/'hy3dgen/shapegen').is_dir():raise FileNotFoundError('Missing local generator source')
    os.environ.setdefault('HF_HUB_OFFLINE','1');os.environ.setdefault('TRANSFORMERS_OFFLINE','1')
    sys.path.insert(0,str(a.source.resolve()))
    import torch
    from PIL import Image
    from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
    from hunyuan_compat import patch
    if patch(a.source)['patch_needed']:raise RuntimeError('Check/apply the compatibility patch before generation')
    image=Image.open(a.image).convert('RGBA')
    if image.getchannel('A').getextrema()[0]==255 and not a.allow_opaque:
        raise ValueError('Image has no transparent pixels; inspect/background-isolate it or explicitly allow an opaque reference')
    device=('cuda' if torch.cuda.is_available() else 'cpu') if a.device=='auto' else a.device
    dtype=torch.float16 if device=='cuda' else torch.float32
    torch.set_num_threads(a.threads);torch.set_default_dtype(dtype);started=time.monotonic()
    pipeline=Hunyuan3DDiTFlowMatchingPipeline.from_single_file(str(a.checkpoint/'model.fp16.safetensors'),
        str(a.checkpoint/'config.yaml'),device='cpu',dtype=dtype,use_safetensors=True)
    if device=='cuda':
        pipeline.components={'conditioner':pipeline.conditioner,'model':pipeline.model,'vae':pipeline.vae}
        pipeline.enable_model_cpu_offload(device='cuda')
    pipeline.vae.enable_flashvdm_decoder(enabled=True,adaptive_kv_selection=False,mc_algo='mc')
    pipeline.device=torch.device(device)
    with torch.inference_mode():
        mesh=pipeline(image=image,num_inference_steps=a.steps,guidance_scale=5.5,
            generator=torch.Generator(device='cpu').manual_seed(a.seed),octree_resolution=a.resolution,
            num_chunks=a.chunks,mc_algo='mc',output_type='trimesh')[0]
    if mesh is None:raise RuntimeError('Generator returned no geometry')
    components=mesh.split(only_watertight=False)
    if a.largest_component and components:mesh=max(components,key=lambda c:len(c.faces))
    a.output.parent.mkdir(parents=True,exist_ok=True);mesh.export(a.output)
    report={'image':str(a.image),'image_sha256':hashlib.sha256(a.image.read_bytes()).hexdigest(),
        'output':str(a.output),'seed':a.seed,'steps':a.steps,'resolution':a.resolution,'chunks':a.chunks,
        'vertices':len(mesh.vertices),'triangles':len(mesh.faces),'components_before_cleanup':len(components),
        'largest_component_only':a.largest_component,'bounds':mesh.bounds.tolist(),'watertight':bool(mesh.is_watertight),
        'torch':torch.__version__,'device':device,'seconds':time.monotonic()-started,
        'stage':'Unrigged generated geometry; topology, material, likeness and deformation review required'}
    a.output.with_suffix(a.output.suffix+'.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2));pipeline.maybe_free_model_hooks();gc.collect()
    if device=='cuda':torch.cuda.empty_cache()

if __name__=='__main__':main()
